-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 18, 2025 at 12:49 AM
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
-- Database: `tomma`
--

-- --------------------------------------------------------

--
-- Table structure for table `portfolios`
--

CREATE TABLE `portfolios` (
  `id` int(11) NOT NULL,
  `nama_proyek` varchar(100) NOT NULL,
  `klien` varchar(100) NOT NULL,
  `deskripsi` text NOT NULL,
  `gambar` varchar(255) NOT NULL,
  `teknologi` varchar(255) NOT NULL,
  `tahun` year(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `requests`
--

CREATE TABLE `requests` (
  `id` int(11) NOT NULL,
  `nama` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `nomor_hp` varchar(20) NOT NULL,
  `tipe_aplikasi` varchar(50) NOT NULL,
  `deskripsi` text NOT NULL,
  `status` enum('baru','diproses','selesai','ditolak') NOT NULL,
  `tanggal` datetime NOT NULL,
  `bukti_dp` varchar(255) DEFAULT NULL,
  `dp_nominal` int(11) DEFAULT NULL,
  `dp_terbayar` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `requests`
--

INSERT INTO `requests` (`id`, `nama`, `email`, `nomor_hp`, `tipe_aplikasi`, `deskripsi`, `status`, `tanggal`, `bukti_dp`, `dp_nominal`, `dp_terbayar`) VALUES
(1, 'Adi', 'adip98816@gmail.com', '09', 'website', '-', 'baru', '2025-06-15 14:09:00', '', 0, 0),
(2, 'Andi', 'andi@gmail.com', '000900', 'konsultasi', '-', 'baru', '2025-06-15 14:33:18', '', 0, 0),
(3, 'Adi', 'adip98816@gmail.com', '081240389409', 'website', '-', 'baru', '2025-06-15 21:04:18', '', 0, 0),
(4, 'Ari', 'ari222@gmail.com', '081240389409', 'website', '-', 'baru', '2025-06-15 21:05:41', '', 0, 0),
(5, 'Andini', 'andini12@gmail.com', '081240389409', 'mobile-app', '-', 'baru', '2025-06-16 12:16:19', NULL, NULL, 0),
(6, 'Andini', 'andini13@gmail.com', '081240389409', 'mobile-app', '-', 'baru', '2025-06-16 12:27:20', NULL, NULL, 0),
(7, 'andi', 'andi@gmail.com', '081240389409', 'network', '-', 'baru', '2025-06-16 12:30:35', NULL, NULL, 0),
(8, 'Andi', 'andi00@gmail.com', '081240389409', 'hosting-server', '-', 'baru', '2025-06-16 12:41:59', NULL, NULL, 0),
(9, 'Andi', 'andi009@gmail.com', '081240389409', 'konsultasi', '-', 'baru', '2025-06-16 12:43:34', NULL, NULL, 0);

-- --------------------------------------------------------

--
-- Table structure for table `services`
--

CREATE TABLE `services` (
  `id` int(11) NOT NULL,
  `judul` varchar(100) NOT NULL,
  `deskripsi` text NOT NULL,
  `ikon` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `testimonials`
--

CREATE TABLE `testimonials` (
  `id` int(11) NOT NULL,
  `nama` varchar(100) NOT NULL,
  `jabatan` varchar(100) NOT NULL,
  `foto` varchar(255) NOT NULL,
  `ulasan` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `nama_lengkap` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `jenis_kelamin` varchar(255) DEFAULT NULL,
  `usia` varchar(255) DEFAULT NULL,
  `foto` varchar(255) NOT NULL,
  `nomor_hp` varchar(255) DEFAULT NULL,
  `level` enum('admin','user') NOT NULL,
  `reset_token` varchar(255) DEFAULT NULL,
  `token_exp` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `nama_lengkap`, `email`, `jenis_kelamin`, `usia`, `foto`, `nomor_hp`, `level`, `reset_token`, `token_exp`) VALUES
(10, 'adip98816_6984', 'pbkdf2:sha256:1000000$Ti20nbTdyoV3ILWL$b97c81ab2fdb852d37866d88f9ae24ecc19fd627c78bd1b6b239f4f5a0eb671e', 'Adhy Prasetyo', 'adip98816@gmail.com', NULL, NULL, 'https://lh3.googleusercontent.com/a/ACg8ocIZbPS94gyLY8YZA1terogtZlCSDWWif7wnqKf3QvvvBF2rutSf=s96-c', NULL, 'user', '', '2025-06-17 23:21:25');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `portfolios`
--
ALTER TABLE `portfolios`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `requests`
--
ALTER TABLE `requests`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `services`
--
ALTER TABLE `services`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `testimonials`
--
ALTER TABLE `testimonials`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `portfolios`
--
ALTER TABLE `portfolios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `requests`
--
ALTER TABLE `requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `services`
--
ALTER TABLE `services`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `testimonials`
--
ALTER TABLE `testimonials`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
