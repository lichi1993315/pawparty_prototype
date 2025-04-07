# 猫咪小镇 (Cat Town) ASCII Prototype

An ASCII-based farm simulation game inspired by Stardew Valley, created with Pygame.

## Game Features

- ASCII-based graphics for a minimalist, retro aesthetic
- Core farming mechanics: tilling soil, planting seeds, watering crops, and harvesting
- Fishing system with fish spots and catching mechanics
- Foraging for wild resources
- Cat companion with affection and hunger systems
- Time and season progression
- Energy management system

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Pygame library

### Installation

1. Clone this repository or download the source code
2. Install the required dependencies:

```bash
pip install pygame
```

3. Run the game:

```bash
python main.py
```

## Controls

- **W/A/S/D**: Move character
- **Space**: Use currently selected tool
- **E**: Interact (harvest crops, collect forage, pet cat)
- **I**: Toggle inventory view
- **1**: Select hoe tool
- **2**: Select watering can
- **3**: Select seeds for planting
- **4**: Select fishing rod
- **5**: Feed cat
- **Enter**: Sleep (when at home and at night)
- **Esc**: Quit game

## Game Mechanics

### Farming
1. Use the hoe (1) to till soil
2. Water tilled soil with watering can (2)
3. Plant seeds (3)
4. Water daily until crops grow
5. Harvest with interaction key (E)

### Fishing
1. Find water tiles marked with 'f' (fish spots)
2. Equip fishing rod (4)
3. Press Space to start fishing
4. Continue pressing Space to increase chance of catching fish

### Cat Care
1. Feed your cat (5) when its hunger is low
2. Pet your cat (E) when nearby to increase affection
3. As affection increases, your cat will unlock special skills to help you

### Daily Routine
- Manage your energy throughout the day
- Return home to sleep at night to restore energy
- If your energy runs out, you'll pass out and return home

## Development

This is a prototype version with minimal features. Future developments may include:
- Improved graphics and animations
- More sophisticated NPC interactions
- Additional farm animals
- Expanded farming and crafting systems 