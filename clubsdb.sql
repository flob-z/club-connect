-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 03, 2025 at 09:17 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `clubsdb`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin') DEFAULT 'admin'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `name`, `email`, `password`, `role`) VALUES
(1, 'Admin User', 'admin@example.com', 'scrypt:32768:8:1$F5odKmrsIf72hvGB$217cd68b918de186bf373a150d5914e8e14424252ec84dad1ca44bd99c668d14ea88ec2be6b030c1e13b952a3f8dcf9be8d8153187b24f27934420e1f58735b9', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `clubs`
--

CREATE TABLE `clubs` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `category` varchar(50) NOT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `is_favorite` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `clubs`
--

INSERT INTO `clubs` (`id`, `name`, `description`, `category`, `image_url`, `is_favorite`) VALUES
(1, 'Pharmacy Students Association', 'A club for pharmacy students to engage in professional development.', 'Academic', NULL, 1),
(2, 'Medical Laboratory Students Association', 'A platform for medical lab students to exchange knowledge.', 'Academic', NULL, 0),
(3, 'Community Health Students Association', 'Promotes community health awareness and initiatives.', 'Health', NULL, 0),
(4, 'Hospitality and Tourism Association', 'For students passionate about hospitality and tourism.', 'Professional', NULL, 0),
(5, 'Dental Technology Students Association', 'Brings together dental technology students for learning and networking.', 'Academic', NULL, 0),
(6, 'Public Health Students Association', 'Focuses on public health awareness and activities.', 'Health', NULL, 0),
(7, 'Information Technology Students Association', 'A club for IT students interested in software and hardware technologies.', 'Technology', NULL, 0),
(8, 'Biomedical Laboratory Students Association', 'Supports biomedical lab students in research and networking.', 'Academic', NULL, 0),
(9, 'Management Science Students Association', 'A club for management and business students.', 'Business', NULL, 0),
(10, 'Animal Health Students Association', 'Dedicated to animal health and veterinary studies.', 'Health', NULL, 0),
(11, 'I Choose Life Movement', 'A youth movement promoting positive life choices.', 'Social', NULL, 0),
(12, 'Business Executives', 'A network for aspiring business leaders and entrepreneurs.', 'Business', NULL, 0),
(13, 'Journalism Club', 'Enhances journalism and media skills among students.', 'Media', NULL, 0),
(14, 'Debate Club', 'A club for students passionate about debating and public speaking.', 'Social', NULL, 0),
(15, 'Journeys Club', 'Explores different cultures and life experiences.', 'Cultural', NULL, 0),
(16, 'Scouts Club', 'Encourages discipline, outdoor activities, and teamwork.', 'Adventure', NULL, 0),
(17, 'Environmental Club', 'Promotes sustainability and environmental conservation.', 'Environment', NULL, 0),
(18, 'Red Cross Society', 'Provides humanitarian aid and emergency response training.', 'Humanitarian', NULL, 0),
(19, 'Bird Watchers Club', 'For students interested in birdwatching and conservation.', 'Nature', NULL, 0),
(20, 'MKU Alumni Association', 'Connects MKU graduates and fosters networking.', 'Networking', NULL, 0),
(21, 'Clinical Medicine Trainees Association', 'A professional platform for clinical medicine students.', 'Health', NULL, 0),
(22, 'Muslim Students Association', 'A faith-based association for Muslim students.', 'Religious', NULL, 0),
(23, 'Young Catholic Society', 'A club for Catholic students to grow spiritually.', 'Religious', NULL, 1),
(24, 'Christian Union', 'A Christian fellowship for worship and study.', 'Religious', NULL, 0),
(25, 'Seventh Day Adventists Group', 'A club for Seventh-Day Adventist students.', 'Religious', NULL, 0),
(26, 'Peace Club', 'Promotes peace and conflict resolution among students.', 'Social', NULL, 0),
(27, 'Rover Club', 'A scouting group for adventure and leadership.', 'Adventure', NULL, 0),
(28, 'Divas of MKU Club', 'Empowers female students in leadership and self-development.', 'Empowerment', NULL, 0);

-- --------------------------------------------------------

--
-- Table structure for table `club_ratings`
--

CREATE TABLE `club_ratings` (
  `id` int(11) NOT NULL,
  `club_id` int(11) NOT NULL,
  `rating` float NOT NULL CHECK (`rating` between 1 and 5),
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `club_ratings`
--

INSERT INTO `club_ratings` (`id`, `club_id`, `rating`, `user_id`) VALUES
(7, 3, 3, 1),
(8, 5, 5, 1),
(9, 2, 3, 1),
(10, 1, 5, 1);

-- --------------------------------------------------------

--
-- Table structure for table `club_reviews`
--

CREATE TABLE `club_reviews` (
  `id` int(11) NOT NULL,
  `club_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `rating` int(11) DEFAULT NULL CHECK (`rating` between 1 and 5),
  `review_text` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `events`
--

CREATE TABLE `events` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `date` datetime NOT NULL,
  `location` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `events`
--

INSERT INTO `events` (`id`, `name`, `description`, `date`, `location`, `created_at`) VALUES
(1, 'Pharmacy Awareness Camp', 'An awareness camp on pharmaceutical care and drug safety.', '2025-04-10 10:00:00', 'Main Campus Auditorium', '2025-03-12 10:33:03'),
(2, 'Medical Lab Innovations', 'Showcasing the latest innovations in medical laboratory sciences.', '2025-05-05 14:00:00', 'Health Sciences Hall', '2025-03-12 10:33:03'),
(3, 'Community Health Outreach', 'A health check-up and awareness program for the community.', '2025-06-15 09:00:00', 'City Park', '2025-03-12 10:33:03'),
(4, 'Tourism Career Expo', 'Explore career opportunities in the hospitality and tourism industry.', '2025-07-20 11:00:00', 'Hospitality Training Center', '2025-03-12 10:33:03'),
(5, 'Dental Hygiene Workshop', 'A seminar on proper dental care and hygiene practices.', '2025-08-10 15:00:00', 'Dental College Room 3', '2025-03-12 10:33:03'),
(6, 'Public Health Conference', 'Discussion on current public health challenges and solutions.', '2025-09-05 10:00:00', 'Conference Hall A', '2025-03-12 10:33:03'),
(7, 'Tech and AI Symposium', 'A deep dive into emerging trends in information technology and AI.', '2025-10-12 13:00:00', 'IT Block - Room 205', '2025-03-12 10:33:03'),
(8, 'Biomedical Research Day', 'Presentation of biomedical research and advancements.', '2025-11-15 12:00:00', 'Science Lab 1', '2025-03-12 10:33:03'),
(9, 'Business Leadership Forum', 'A networking event for future business executives.', '2025-12-05 16:00:00', 'Business School Hall', '2025-03-12 10:33:03'),
(10, 'Journalism Media Week', 'Workshops on media ethics, reporting, and content creation.', '2026-01-22 10:00:00', 'Mass Communication Lab', '2025-03-12 10:33:03'),
(11, 'Debate Championship', 'An inter-university debate competition.', '2026-02-15 14:00:00', 'Main Hall', '2025-03-12 10:33:03'),
(12, 'Scouting Adventure', 'Outdoor camping and survival skills training.', '2026-03-08 09:00:00', 'National Park', '2025-03-12 10:33:03'),
(13, 'Environmental Cleanup', 'A volunteer event focused on cleaning and conservation.', '2026-04-18 07:00:00', 'Lakeview Park', '2025-03-12 10:33:03'),
(14, 'Red Cross Blood Drive', 'Blood donation campaign for emergency preparedness.', '2026-05-20 11:00:00', 'Health Center', '2025-03-12 10:33:03'),
(15, 'Bird Watching Tour', 'Exploring the region’s rich bird species.', '2026-06-10 06:00:00', 'Forest Reserve', '2025-03-12 10:33:03'),
(16, 'MKU Alumni Meet', 'Networking event for MKU graduates.', '2026-07-05 18:00:00', 'Alumni Center', '2025-03-12 10:33:03'),
(17, 'Clinical Medicine Workshop', 'A hands-on medical procedures training.', '2026-08-12 09:00:00', 'Medical Lab', '2025-03-12 10:33:03'),
(18, 'Islamic Awareness Week', 'Discussions on Islamic teachings and cultural values.', '2026-09-15 13:00:00', 'Muslim Students Center', '2025-03-12 10:33:03'),
(19, 'Christian Union Worship Night', 'A night of praise, worship, and prayer.', '2026-10-22 19:00:00', 'University Chapel', '2025-03-12 10:33:03'),
(20, 'Peace and Conflict Resolution Seminar', 'A seminar on promoting peace and resolving conflicts.', '2026-11-30 15:00:00', 'Lecture Hall 5', '2025-03-12 10:33:03');

-- --------------------------------------------------------

--
-- Table structure for table `event_participants`
--

CREATE TABLE `event_participants` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `registered_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `memberships`
--

CREATE TABLE `memberships` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `club_id` int(11) NOT NULL,
  `joined_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `role` enum('Member','Admin','Moderator') DEFAULT 'Member'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `messages`
--

CREATE TABLE `messages` (
  `id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` varchar(50) NOT NULL DEFAULT 'active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `notification`
--

CREATE TABLE `notification` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `icon` varchar(50) DEFAULT 'bell',
  `is_read` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `user_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notification`
--

INSERT INTO `notification` (`id`, `title`, `message`, `icon`, `is_read`, `created_at`, `user_id`) VALUES
(1, 'Meeting', 'There is a meeting today', 'bell', 1, '2025-03-13 09:55:40', NULL),
(2, 'Drama Alert', 'We have drama today', 'bell', 0, '2025-03-13 10:18:36', NULL),
(3, 'Club meeting', 'Club meeting at 10', 'bell', 0, '2025-03-13 10:30:45', NULL),
(4, 'jkjcbkzvs', 'uuafhwoehf', 'bell', 0, '2025-04-03 14:08:49', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL,
  `department` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `role`, `department`) VALUES
(1, 'John', 'john@gmail.com', '123456', 'Student', 'Computer Science'),
(2, 'Carlos', 'carlos@gmail.com', '123456', 'Student', 'Health'),
(3, 'Richard', 'richard@gmail.com', '123456', 'Admin', 'Admin'),
(4, 'Vance', 'vance@gmail.com', '123456', 'Admin', 'Admin'),
(5, 'Jack', 'jack@gmail.com', '123456', 'Student', 'Finance');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `clubs`
--
ALTER TABLE `clubs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `club_ratings`
--
ALTER TABLE `club_ratings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `club_id` (`club_id`);

--
-- Indexes for table `club_reviews`
--
ALTER TABLE `club_reviews`
  ADD PRIMARY KEY (`id`),
  ADD KEY `club_id` (`club_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `events`
--
ALTER TABLE `events`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `event_participants`
--
ALTER TABLE `event_participants`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `event_id` (`event_id`);

--
-- Indexes for table `memberships`
--
ALTER TABLE `memberships`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `club_id` (`club_id`);

--
-- Indexes for table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sender_id` (`sender_id`),
  ADD KEY `receiver_id` (`receiver_id`);

--
-- Indexes for table `notification`
--
ALTER TABLE `notification`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `clubs`
--
ALTER TABLE `clubs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `club_ratings`
--
ALTER TABLE `club_ratings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `club_reviews`
--
ALTER TABLE `club_reviews`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `events`
--
ALTER TABLE `events`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `event_participants`
--
ALTER TABLE `event_participants`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `memberships`
--
ALTER TABLE `memberships`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `notification`
--
ALTER TABLE `notification`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `club_ratings`
--
ALTER TABLE `club_ratings`
  ADD CONSTRAINT `club_ratings_ibfk_1` FOREIGN KEY (`club_id`) REFERENCES `clubs` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `club_reviews`
--
ALTER TABLE `club_reviews`
  ADD CONSTRAINT `club_reviews_ibfk_1` FOREIGN KEY (`club_id`) REFERENCES `clubs` (`id`),
  ADD CONSTRAINT `club_reviews_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `event_participants`
--
ALTER TABLE `event_participants`
  ADD CONSTRAINT `event_participants_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `event_participants_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `memberships`
--
ALTER TABLE `memberships`
  ADD CONSTRAINT `memberships_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `memberships_ibfk_2` FOREIGN KEY (`club_id`) REFERENCES `clubs` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
