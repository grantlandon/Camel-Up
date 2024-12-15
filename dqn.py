import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from playerinterface import PlayerInterface
from camelup import get_valid_moves, GameState

class DQN(nn.Module):
    def __init__(self, input_size, output_size):
        super(DQN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, output_size)
        )

    def forward(self, x):
        return self.network(x)

class DQNBot(PlayerInterface):
    def __init__(self, state_size, action_size, epsilon=1.0, epsilon_min=0.1, epsilon_decay=0.995, gamma=0.99):
        self.state_size = state_size
        self.action_size = action_size
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.gamma = gamma
        self.memory = deque(maxlen=2000)
        self.model = DQN(state_size, action_size)
        self.target_model = DQN(state_size, action_size)
        self.update_target_model()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.last_coin_count = 0  # Track coin count from previous state

    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def calculate_reward(self, current_coin_count):
        # Calculate reward as the difference in coin count
        reward = current_coin_count - self.last_coin_count
        self.last_coin_count = current_coin_count  # Update for next calculation
        return reward

    def act(self, state, valid_moves):
        if np.random.rand() <= self.epsilon:
            return random.choice(valid_moves)
        
        state = torch.FloatTensor(state).unsqueeze(0)
        q_values = self.model(state)
        
        # Masking invalid moves by setting their Q-values to a large negative number
        q_values = q_values.detach().numpy().flatten()
        masked_q_values = [q_values[action] if action in valid_moves else -np.inf for action in range(self.action_size)]
        
        return np.argmax(masked_q_values)

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            state = torch.FloatTensor(state)
            next_state = torch.FloatTensor(next_state)
            target = reward
            if not done:
                target += self.gamma * torch.max(self.target_model(next_state)).item()
            
            target_f = self.model(state)
            target_f[action] = target
            
            self.optimizer.zero_grad()
            loss = nn.MSELoss()(self.model(state), target_f)
            loss.backward()
            self.optimizer.step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def move(self, active_player, game_state):
        state = self.summarize_game_state(game_state)  # Summarize the game state
        valid_moves = get_valid_moves(game_state, active_player)
        
        action = self.act(state, valid_moves)
        
        # Calculate the coin-based reward
        current_coin_count = game_state.player_money_values[active_player]
        reward = self.calculate_reward(current_coin_count)
        
        # Store the experience for training
        next_state = self.summarize_game_state(game_state)
        done = not game_state.active_game
        self.remember(state, action, reward, next_state, done)
        
        return valid_moves[action] if action in valid_moves else random.choice(valid_moves)
    
    def summarize_game_state(self, game_state):
        """
        Summarize the game state into a fixed-size numerical array.
        This includes camel positions, camels yet to move, trap locations, and player coin counts.
        """
        summary = []

        # Camel positions: each position on the track can have a stack of camels.
        # We could represent each position as the list of camel IDs in that position, filling gaps as needed.
        for position in game_state.camel_track:
            # Encode the camel stack at each position (0 if no camel at that position)
            summary.extend([camel if camel is not None else 0 for camel in position])
        
        # Camels yet to move: 1 if camel hasn't moved this round, 0 if it has moved.
        summary.extend([1 if yet_to_move else 0 for yet_to_move in game_state.camel_yet_to_move])

        # Trap locations: Track if a trap is at each position, and its type if present.
        for trap in game_state.trap_track:
            if trap:
                trap_type, player_id = trap
                summary.extend([trap_type, player_id])
            else:
                summary.extend([0, -1])  # No trap and no associated player for empty positions

        # Player coin counts (the bot might use this information to strategize for maximizing coins)
        summary.extend(game_state.player_money_values)

        return summary
