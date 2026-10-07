-- =====================================================================
-- ESCAPE ROOM DATABASE SCHEMA & SEED DATA
-- Course: DBMS (Sem 3)
-- Relational Model with 3NF Normalization & Multimedia Clues
-- =====================================================================

CREATE DATABASE IF NOT EXISTS `escape_room`;
USE `escape_room`;

-- ---------------------------------------------------------------------
-- Table: rooms
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `rooms` (
  `room_id` int NOT NULL AUTO_INCREMENT,
  `room_name` varchar(100) NOT NULL,
  `theme` varchar(50) NOT NULL,
  `difficulty` varchar(20) NOT NULL,
  `time_limit` int NOT NULL,
  PRIMARY KEY (`room_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------------
-- Table: puzzles
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `puzzles` (
  `puzzle_id` int NOT NULL AUTO_INCREMENT,
  `room_id` int NOT NULL,
  `puzzle_name` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `answer` varchar(100) NOT NULL,
  `points` int NOT NULL,
  `sequence_no` int NOT NULL,
  `difficulty` varchar(20) NOT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`puzzle_id`),
  UNIQUE KEY `room_id_sequence` (`room_id`,`sequence_no`),
  CONSTRAINT `puzzles_ibfk_1` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`room_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------------
-- Table: clues
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `clues` (
  `clue_id` int NOT NULL AUTO_INCREMENT,
  `puzzle_id` int NOT NULL,
  `clue_text` text NOT NULL,
  `point_penalty` int NOT NULL,
  PRIMARY KEY (`clue_id`),
  KEY `puzzle_id` (`puzzle_id`),
  CONSTRAINT `clues_ibfk_1` FOREIGN KEY (`puzzle_id`) REFERENCES `puzzles` (`puzzle_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------------
-- Table: teams
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `teams` (
  `team_id` int NOT NULL AUTO_INCREMENT,
  `team_name` varchar(100) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`team_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------------
-- Table: players
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `players` (
  `player_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `experience_level` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`player_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------------
-- Table: team_members
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `team_members` (
  `team_id` int NOT NULL,
  `player_id` int NOT NULL,
  `joined_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`team_id`,`player_id`),
  KEY `player_id` (`player_id`),
  CONSTRAINT `team_members_ibfk_1` FOREIGN KEY (`team_id`) REFERENCES `teams` (`team_id`) ON DELETE CASCADE,
  CONSTRAINT `team_members_ibfk_2` FOREIGN KEY (`player_id`) REFERENCES `players` (`player_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------------
-- Table: game_sessions
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `game_sessions` (
  `session_id` int NOT NULL AUTO_INCREMENT,
  `team_id` int NOT NULL,
  `room_id` int NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime DEFAULT NULL,
  `status` varchar(20) DEFAULT 'ACTIVE',
  `final_score` int DEFAULT '0',
  PRIMARY KEY (`session_id`),
  KEY `team_id` (`team_id`),
  KEY `room_id` (`room_id`),
  CONSTRAINT `game_sessions_ibfk_1` FOREIGN KEY (`team_id`) REFERENCES `teams` (`team_id`),
  CONSTRAINT `game_sessions_ibfk_2` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`room_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------------
-- Table: puzzle_attempts
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `puzzle_attempts` (
  `attempt_id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `puzzle_id` int NOT NULL,
  `answer_submitted` varchar(100) NOT NULL,
  `attempt_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `is_correct` tinyint(1) NOT NULL,
  PRIMARY KEY (`attempt_id`),
  KEY `session_id` (`session_id`),
  KEY `puzzle_id` (`puzzle_id`),
  CONSTRAINT `puzzle_attempts_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `game_sessions` (`session_id`) ON DELETE CASCADE,
  CONSTRAINT `puzzle_attempts_ibfk_2` FOREIGN KEY (`puzzle_id`) REFERENCES `puzzles` (`puzzle_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------------
-- Table: hints_used
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `hints_used` (
  `hint_usage_id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `clue_id` int NOT NULL,
  `used_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `points_lost` int NOT NULL,
  PRIMARY KEY (`hint_usage_id`),
  KEY `session_id` (`session_id`),
  KEY `clue_id` (`clue_id`),
  CONSTRAINT `hints_used_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `game_sessions` (`session_id`) ON DELETE CASCADE,
  CONSTRAINT `hints_used_ibfk_2` FOREIGN KEY (`clue_id`) REFERENCES `clues` (`clue_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------------
-- View: leaderboard
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW `leaderboard` AS
SELECT 
  `t`.`team_id` AS `team_id`,
  `t`.`team_name` AS `team_name`,
  COUNT(`gs`.`session_id`) AS `games_played`,
  COALESCE(SUM(CASE WHEN `gs`.`status` = 'ESCAPED' THEN 1 ELSE 0 END), 0) AS `games_escaped`,
  COALESCE(MAX(`gs`.`final_score`), 0) AS `highest_score`,
  COALESCE(AVG(`gs`.`final_score`), 0.0) AS `average_score`
FROM `teams` `t`
LEFT JOIN `game_sessions` `gs` ON `t`.`team_id` = `gs`.`team_id`
GROUP BY `t`.`team_id`, `t`.`team_name`;

-- ---------------------------------------------------------------------
-- Seed: rooms (Top 3 Detailed Themed Escape Rooms)
-- ---------------------------------------------------------------------
INSERT INTO `rooms` (`room_id`, `room_name`, `theme`, `difficulty`, `time_limit`) VALUES
(1, 'The Haunted Manor', 'Horror', 'Hard', 30),
(2, 'The Lost Temple', 'Adventure', 'Medium', 25),
(3, 'Space Station Omega', 'Sci-Fi', 'Hard', 30)
ON DUPLICATE KEY UPDATE 
  `room_name`=VALUES(`room_name`),
  `theme`=VALUES(`theme`),
  `difficulty`=VALUES(`difficulty`),
  `time_limit`=VALUES(`time_limit`);

-- ---------------------------------------------------------------------
-- Seed: puzzles (5 Solvable Stages per Room with Visual Clues)
-- ---------------------------------------------------------------------
INSERT INTO `puzzles` (`puzzle_id`, `room_id`, `puzzle_name`, `description`, `answer`, `points`, `sequence_no`, `difficulty`, `image_path`) VALUES
-- Room 1: The Haunted Manor
(1, 1, 'The Broken Clock', 'A grandfather clock has stopped at a strange time in the shadows of the manor. Examine the clock face and painting closely to deduce the four-digit code.', '1843', 100, 1, 'Medium', 'images/room1_p1.png'),
(2, 1, 'The Locked Drawer', 'An ornate brass lock on the study desk requires an 8-letter word. A riddle is scratched into the aged wood:\n"I am the witching hour where yesterday dies and tomorrow is born, when darkness is deepest and shadows mourn. Twelve strikes of the bell seal my name. What hour am I?"', 'MIDNIGHT', 100, 2, 'Medium', 'images/room1_p2.jpg'),
(3, 1, 'The Photograph', 'Inside the desk drawer lies an antique photograph. On the back is penned:\n"Nevermore I speak in Poe\'s dark rhyme, a black-feathered omen perched through time. Five letters spell the watcher of the gloom." What bird watches the manor?', 'RAVEN', 100, 3, 'Medium', 'images/room1_p3.jpg'),
(4, 1, 'The Hidden Library', 'A secret bookshelf shifts open to reveal a cipher engraved above the archway:\n"THE KEY TO EXIT LIES NOT IN LIGHT, BUT WHERE SHADOWS HIDE FROM SIGHT." Step into the candle flame and I stretch tall behind you. What am I?', 'SHADOW', 100, 4, 'Hard', 'images/room1_p4.jpg'),
(5, 1, 'The Final Door', 'The iron exit of the manor bears a final riddle on the family crest:\n"Beside the misty graveyard I weep in the breeze, bowing my long green branches beneath the cold trees. What weeping tree guards the manor gates?"', 'WILLOW', 150, 5, 'Hard', 'images/room1_p5.jpg'),

-- Room 2: The Lost Temple
(6, 2, 'Ancient Inscription', 'Carved into the sandstone temple wall are reliefs of four sacred beasts in descending order of power: Elephant (4 tusks), Lion (3 claws), Cobra (2 fangs), and Falcon (1 talon). The glyph states: "Order the beasts from greatest to least to enter." Enter the 4-digit code:', '4321', 100, 1, 'Medium', 'images/room2_p1.jpg'),
(7, 2, 'The Stone Lock', 'A circular stone basin is surrounded by carved aquatic petals. The riddle reads:\n"Rooted in mud, I rise untouched and pure. Unfolding on water, an emblem serene and sure. Five letters spell the sacred flower of enlightenment." What flower unlocks the chamber?', 'LOTUS', 100, 2, 'Medium', 'images/room2_p2.jpg'),
(8, 2, 'The Guardian Statue', 'A colossal Sun Guardian statue speaks:\n"Kings and conquerors journeyed far to seek my sight. I unveil the unwritten future and pierce mortal night. In Delphi they knelt before my word. What ancient seer am I?"', 'ORACLE', 100, 3, 'Medium', 'images/room2_p3.jpg'),
(9, 2, 'Sacred Symbols', 'Six stone pillars in the temple hall bear Caesar cipher runes: "U - F - N - Q - M - F".\nShift each letter backward by 1 position (B->A, C->B) to reveal the sanctuary\'s sacred keyword:', 'TEMPLE', 100, 4, 'Medium', 'images/room2_p4.jpg'),
(10, 2, 'The Artifact Vault', 'The golden altar scale in the treasure chamber asks:\n"Heavier than silver, prized by Pharaohs of old; I never tarnish nor rust, radiant and bold. What four-letter precious element balances the altar?"', 'GOLD', 150, 5, 'Hard', 'images/room2_p5.jpg'),

-- Room 3: Space Station Omega
(11, 3, 'Emergency Transmission', 'The station console flashes a distress transmission encoded in NATO phonetic letters:\n"OSCAR - MIKE - ECHO - GOLF - ALPHA". Enter the decoded mission codeword:', 'OMEGA', 100, 1, 'Medium', 'images/room3_p1.jpg'),
(12, 3, 'Power Core', 'Stabilize the plasma reactor frequency. Four diagnostic readouts are visible on the core monitors:\nCore A: 7, Core B: 3, Core C: 9, Core D: 1. What is the 4-digit reactor frequency?', '7391', 100, 2, 'Medium', 'images/room3_p2.jpg'),
(13, 3, 'Oxygen System', 'The life-support terminal prompts for the essential element:\n"Atomic number 8, the lifeblood of terrestrial breath. Without me, crew hypoxia leads to frozen death. Symbol O on the periodic table." Enter the elemental gas name:', 'OXYGEN', 100, 3, 'Medium', 'images/room3_p3.jpg'),
(14, 3, 'Navigation Console', 'The orbital nav-computer displays the target planet:\n"Fourth world from the Sun, bearing rusty red sands and towering Olympus Mons. Named after the ancient Roman god of war." Enter the planet name:', 'MARS', 100, 4, 'Medium', 'images/room3_p4.jpg'),
(15, 3, 'Escape Pod', 'The final authorization command is needed to fire the pod thrusters:\n"L _ _ _ C H: Six-letter command word that fires the thrusters and propels the capsule to safety." Enter the command:', 'LAUNCH', 150, 5, 'Hard', 'images/room3_p5.png')
ON DUPLICATE KEY UPDATE
  `puzzle_name`=VALUES(`puzzle_name`),
  `description`=VALUES(`description`),
  `answer`=VALUES(`answer`),
  `points`=VALUES(`points`),
  `difficulty`=VALUES(`difficulty`),
  `image_path`=VALUES(`image_path`);

-- ---------------------------------------------------------------------
-- Seed: clues (30 Graded Clues with Point Penalties)
-- ---------------------------------------------------------------------
INSERT INTO `clues` (`clue_id`, `puzzle_id`, `clue_text`, `point_penalty`) VALUES
(1, 1, 'Look closely at the stopped clock and the painting beside it.', 10),
(2, 1, 'The four numbers are connected to the time shown by the clock (18:43).', 20),
(3, 2, 'Think about the time when darkness is deepest (12:00 AM midnight).', 10),
(4, 2, 'Eight letters: M - I - D - N - I - G - H - T.', 20),
(5, 3, 'Look carefully at the creature perched in the antique photograph.', 10),
(6, 3, 'Think of Edgar Allan Poe\'s famous dark raven: "Quoth the Raven, Nevermore".', 20),
(7, 4, 'Read the illuminated inscription above the archway in the image.', 10),
(8, 4, 'It follows you in the light and disappears in the dark: S - H - A - D - O - W.', 20),
(9, 5, 'Look at the weeping tree flanking the iron gate in the visual.', 10),
(10, 5, 'A weeping tree: W - I - L - L - O - W.', 20),
(11, 6, 'Count the features on each beast from 4 down to 1.', 10),
(12, 6, 'Reverse order from greatest to least: 4, 3, 2, 1.', 20),
(13, 7, 'Look at the glowing aquatic flower floating in the carved basin.', 10),
(14, 7, 'Five letters starting with L: L - O - T - U - S.', 20),
(15, 8, 'A prophet or seer from ancient Delphi with glowing sight.', 10),
(16, 8, 'Six letters: O - R - A - C - L - E.', 20),
(17, 9, 'Shift each letter on the stone pillars one position backward (U->T, F->E).', 10),
(18, 9, 'The keyword is T - E - M - P - L - E.', 20),
(19, 10, 'A precious yellow metal represented by Au on the balance scale.', 10),
(20, 10, 'Four letters: G - O - L - D.', 20),
(21, 11, 'Take the first letter of each NATO phonetic word: O, M, E, G, A.', 10),
(22, 11, 'Codeword is O - M - E - G - A.', 20),
(23, 12, 'Read the values directly from Core A, B, C, and D on the monitors.', 10),
(24, 12, 'The 4-digit code is 7 - 3 - 9 - 1.', 20),
(25, 13, 'The chemical element with symbol O and atomic number 8.', 10),
(26, 13, 'The breathable life support gas: O - X - Y - G - E - N.', 20),
(27, 14, 'The famous Red Planet with Olympus Mons, 4th from the Sun.', 10),
(28, 14, 'Four letters: M - A - R - S.', 20),
(29, 15, 'Look at the authorization prompt: L _ _ _ C H.', 10),
(30, 15, 'Six-letter command: L - A - U - N - C - H.', 20)
ON DUPLICATE KEY UPDATE
  `clue_text`=VALUES(`clue_text`),
  `point_penalty`=VALUES(`point_penalty`);

-- ---------------------------------------------------------------------
-- Seed: sample teams, players, memberships, and sessions
-- ---------------------------------------------------------------------
INSERT INTO `teams` (`team_id`, `team_name`) VALUES
(1, 'The Brainy Bunch'),
(2, 'Code Breakers'),
(3, 'Shadow Hunters'),
(4, 'The Escape Artists'),
(5, 'dbmstoppers')
ON DUPLICATE KEY UPDATE `team_name`=VALUES(`team_name`);

INSERT INTO `players` (`player_id`, `name`, `email`, `experience_level`) VALUES
(1, 'Aarav Sharma', 'aarav@gmail.com', 'Beginner'),
(2, 'Ishita Verma', 'ishita@gmail.com', 'Intermediate'),
(3, 'Rohan Mehta', 'rohan@gmail.com', 'Expert'),
(4, 'Ananya Kapoor', 'ananya@gmail.com', 'Intermediate'),
(5, 'Kabir Singh', 'kabir@gmail.com', 'Beginner'),
(6, 'Meera Joshi', 'meera@gmail.com', 'Expert'),
(7, 'Arjun Malhotra', 'arjun@gmail.com', 'Intermediate'),
(8, 'Siya Agarwal', 'siya@gmail.com', 'Beginner'),
(9, 'Vihaan Gupta', 'vihaan@gmail.com', 'Expert'),
(10, 'Tara Khanna', 'tara@gmail.com', 'Intermediate')
ON DUPLICATE KEY UPDATE 
  `name`=VALUES(`name`),
  `experience_level`=VALUES(`experience_level`);

INSERT INTO `team_members` (`team_id`, `player_id`) VALUES
(1, 1), (1, 2), (1, 3),
(2, 4), (2, 5),
(3, 6), (3, 7), (3, 8),
(4, 9), (4, 10)
ON DUPLICATE KEY UPDATE `team_id`=VALUES(`team_id`);

INSERT INTO `game_sessions` (`session_id`, `team_id`, `room_id`, `start_time`, `end_time`, `status`, `final_score`) VALUES
(1, 1, 1, '2026-09-01 10:00:00', '2026-09-01 10:28:00', 'ESCAPED', 420),
(2, 2, 2, '2026-09-02 14:00:00', '2026-09-02 14:24:00', 'ESCAPED', 450),
(3, 3, 1, '2026-09-03 10:00:00', '2026-09-03 10:29:00', 'ESCAPED', 350),
(4, 3, 2, '2026-09-04 13:00:00', '2026-09-04 13:23:00', 'ESCAPED', 460),
(5, 4, 3, '2026-09-05 12:00:00', '2026-09-05 12:27:00', 'ESCAPED', 400)
ON DUPLICATE KEY UPDATE 
  `room_id`=VALUES(`room_id`),
  `status`=VALUES(`status`),
  `final_score`=VALUES(`final_score`);
