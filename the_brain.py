import numpy as np
import random
from keras.models import Sequential
from keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Flatten
from keras.optimizers import Adam
from keras.losses import Huber

from collections import deque

from scipy import ndimage

def block_mean(ar, fact):
    assert isinstance(fact, int), type(fact)
    sx, sy = ar.shape
    X, Y = np.ogrid[0:sx, 0:sy]
    regions = sy//fact * (X//fact) + Y//fact
    res = ndimage.mean(ar, labels=regions, index=np.arange(regions.max() + 1))
    res.shape = (sx//fact, sy//fact)
    return res

def rgb2gray(img):
    R = img[:, :, 0]
    G = img[:, :, 1]
    B = img[:, :, 2]
    img_gray = R * 299. / 1000 + G * 587. / 1000 + B * 114. / 1000
    return img_gray.astype(np.uint8)

def normalize_img(img):
    return img / 255

class DQN:
    def __init__(self, input_shape, output_shape):
        self.input_shape  = input_shape
        self.output_shape = output_shape
        self.memory  = deque(maxlen=10000)
        self.best_memories = deque(maxlen=100)
        self.random_memories = deque(maxlen=100)
        
        self.gamma = 0.85
        self.epsilon = 1
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.05
        self.tau = .125

        self.model        = self.create_model()
        self.target_model = self.create_model()

    def create_model(self):
        model   = Sequential()
        state_shape  = self.input_shape
        model.add(Conv2D(32, 8, strides=(4, 4), padding="valid",activation="relu", input_shape = state_shape))
        model.add(Conv2D(64, 4, strides=(2, 2), padding="valid",activation="relu", input_shape = state_shape))
        model.add(Conv2D(64, 3, strides=(1, 1), padding="valid",activation="relu", input_shape = state_shape))
        model.add(Flatten())
        model.add(Dense(512, activation="relu"))
        model.add(Dense(self.output_shape))
        model.compile(loss=Huber(),
            optimizer=Adam(lr=self.learning_rate))
        return model

    def act(self, state):
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon_min, self.epsilon)
        if np.random.random() < self.epsilon:
            return np.random.randint(0, self.output_shape)

        state = np.array([state.reshape(self.input_shape)])
        predicted = self.model.predict(state)[0]
        print("I do think ", predicted)
        return np.argmax(predicted)

    def remember(self, state, action, reward, new_state, done):
        self.memory.append([state, action, reward, new_state, done])
    
    def remember_best(self, state, action, reward, new_state, done):
        self.best_memories.append([state, action, reward, new_state, done])

    def remember_random(self, state, action, reward, new_state, done):
        self.random_memories.append([state, action, reward, new_state, done])

    def replay(self):
        batch_size = 32
        memory = []
        memory.extend(self.memory)
        memory.extend(self.best_memories)
        memory.extend(self.random_memories)

        if len(memory) < batch_size: 
            return
        
        samples = random.sample(memory, batch_size)
        for sample in samples:
            state, action, reward, new_state, done = sample
            import matplotlib.pyplot as plt
            #plt.imshow(state, cmap=plt.get_cmap('gray')) #Needs to be in row,col order
            #plt.savefig("old.png")
            #plt.imshow(new_state, cmap=plt.get_cmap('gray')) #Needs to be in row,col order
            #plt.savefig("nou.png")
            target = self.target_model.predict(np.array([state.reshape(self.input_shape)]))
            if done:
                target[0][action] = reward
            else:
                target_model_pred = self.target_model.predict(np.array([new_state.reshape(self.input_shape)]))
                Q_future = max(target_model_pred[0])
                target[0][action] = reward + Q_future * self.gamma
            self.model.fit(np.array([state.reshape(self.input_shape)]), target, epochs=1, verbose=0)

    def target_train(self):
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(target_weights)):
            target_weights[i] = weights[i] * self.tau + target_weights[i] * (1 - self.tau)
        self.target_model.set_weights(target_weights)

    def save_model(self, fn):
        self.model.save(fn)

def main():
    env     = gym.make("MountainCar-v0")
    gamma   = 0.9
    epsilon = .95

    trials  = 1000
    trial_len = 500

    # updateTargetNetwork = 1000
    dqn_agent = DQN(env=env)
    steps = []
    for trial in range(trials):
        cur_state = env.reset().reshape(1,2)
        for step in range(trial_len):
            action = dqn_agent.act(cur_state)
            new_state, reward, done, _ = env.step(action)

            # reward = reward if not done else -20
            new_state = new_state.reshape(1,2)
            dqn_agent.remember(cur_state, action, reward, new_state, done)
            
            dqn_agent.replay()       # internally iterates default (prediction) model
            dqn_agent.target_train() # iterates target model

            cur_state = new_state
            if done:
                break
        if step >= 199:
            print("Failed to complete in trial {}".format(trial))
            if step % 10 == 0:
                dqn_agent.save_model("trial-{}.model".format(trial))
        else:
            print("Completed in {} trials".format(trial))
            dqn_agent.save_model("success.model")
            break

if __name__ == "__main__":
    main()