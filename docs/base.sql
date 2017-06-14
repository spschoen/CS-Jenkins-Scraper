-- MySQL dump 10.13  Distrib 5.6.10, for Linux (x86_64)
--
-- Host: localhost    Database: repoinfo
-- ------------------------------------------------------
-- Server version	5.6.10

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `PMD`
--

DROP TABLE IF EXISTS `PMD`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PMD` (
  `CommitUID` int(11) NOT NULL,
  `MethodUID` int(11) NOT NULL,
  `Ruleset` varchar(20) DEFAULT NULL,
  `Rule` varchar(50) DEFAULT NULL,
  `Line` int(11) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PMD`
--

LOCK TABLES `PMD` WRITE;
/*!40000 ALTER TABLE `PMD` DISABLE KEYS */;
/*!40000 ALTER TABLE `PMD` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TS_testTable`
--

DROP TABLE IF EXISTS `TS_testTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TS_testTable` (
  `CommitUID` int(11) NOT NULL DEFAULT '0',
  `testMethodUID` int(11) DEFAULT NULL,
  `Passing` varchar(1) DEFAULT NULL,
  `Message` varchar(500) DEFAULT NULL,
  `Line` int(11) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TS_testTable`
--

LOCK TABLES `TS_testTable` WRITE;
/*!40000 ALTER TABLE `TS_testTable` DISABLE KEYS */;

/*!40000 ALTER TABLE `TS_testTable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `checkstyle`
--

DROP TABLE IF EXISTS `checkstyle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `checkstyle` (
  `CommitUID` int(11) NOT NULL,
  `ClassUID` int(11) DEFAULT NULL,
  `ErrorType` varchar(50) DEFAULT NULL,
  `Severity` varchar(20) DEFAULT NULL,
  `ErrorMessage` varchar(100) DEFAULT NULL,
  `Line` int(11) DEFAULT NULL,
  `Col` int(11) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `checkstyle`
--

LOCK TABLES `checkstyle` WRITE;
/*!40000 ALTER TABLE `checkstyle` DISABLE KEYS */;

/*!40000 ALTER TABLE `checkstyle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classUID`
--

DROP TABLE IF EXISTS `classUID`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `classUID` (
  `classUID` int(11) NOT NULL AUTO_INCREMENT,
  `Package` varchar(50) DEFAULT NULL,
  `Class` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`classUID`)
) ENGINE=MyISAM AUTO_INCREMENT=17 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classUID`
--

LOCK TABLES `classUID` WRITE;
/*!40000 ALTER TABLE `classUID` DISABLE KEYS */;

/*!40000 ALTER TABLE `classUID` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `commitUID`
--

DROP TABLE IF EXISTS `commitUID`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `commitUID` (
  `commitUID` int(11) NOT NULL AUTO_INCREMENT,
  `Hexsha` varchar(40) DEFAULT NULL,
  `Repo` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`commitUID`)
) ENGINE=MyISAM AUTO_INCREMENT=31 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `commitUID`
--

LOCK TABLES `commitUID` WRITE;
/*!40000 ALTER TABLE `commitUID` DISABLE KEYS */;

/*!40000 ALTER TABLE `commitUID` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `commits`
--

DROP TABLE IF EXISTS `commits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `commits` (
  `CommitUID` int(11) NOT NULL AUTO_INCREMENT,
  `Commit_Hash` varchar(40) NOT NULL,
  `Repo` varchar(40) NOT NULL,
  `Build_Num` int(11) DEFAULT NULL,
  `Compile_ST` varchar(1) DEFAULT NULL,
  `Compile_TS` varchar(1) DEFAULT NULL,
  `Author` varchar(8) DEFAULT NULL,
  `Time` int(11) DEFAULT NULL,
  `Duration` int(11) DEFAULT NULL,
  `Message` varchar(50) DEFAULT NULL,
  `Src_Code_Lines` int(11) NOT NULL,
  `Src_Comment_Lines` int(11) NOT NULL,
  `Src_Class_Count` int(11) NOT NULL,
  `Src_Method_Count` int(11) NOT NULL,
  `Test_Code_Lines` int(11) NOT NULL,
  `Test_Comment_Lines` int(11) NOT NULL,
  `Test_Classes` int(11) NOT NULL,
  `Test_Method_Count` int(11) NOT NULL,
  `Assert_Count` int(11) NOT NULL,
  `Commits_Since_Javadoc` int(11) NOT NULL,
  PRIMARY KEY (`CommitUID`)
) ENGINE=MyISAM AUTO_INCREMENT=57 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `commits`
--

LOCK TABLES `commits` WRITE;
/*!40000 ALTER TABLE `commits` DISABLE KEYS */;

/*!40000 ALTER TABLE `commits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coverage`
--

DROP TABLE IF EXISTS `coverage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coverage` (
  `CommitUID` int(11) NOT NULL,
  `ClassUID` int(11) DEFAULT NULL,
  `Line_Coverage` int(11) DEFAULT NULL,
  `Instruction_Coverage` int(11) DEFAULT NULL,
  `Branch_Coverage` int(11) DEFAULT NULL,
  `Complexity_Coverage` int(11) DEFAULT NULL,
  `Method_Coverage` int(11) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coverage`
--

LOCK TABLES `coverage` WRITE;
/*!40000 ALTER TABLE `coverage` DISABLE KEYS */;

/*!40000 ALTER TABLE `coverage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `findBugs`
--

DROP TABLE IF EXISTS `findBugs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `findBugs` (
  `CommitUID` int(11) DEFAULT NULL,
  `MethodUID` int(11) DEFAULT NULL,
  `BugType` varchar(100) DEFAULT NULL,
  `Priority` varchar(20) DEFAULT NULL,
  `Rank` varchar(20) DEFAULT NULL,
  `Category` varchar(20) DEFAULT NULL,
  `Line` int(11) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `findBugs`
--

LOCK TABLES `findBugs` WRITE;
/*!40000 ALTER TABLE `findBugs` DISABLE KEYS */;

/*!40000 ALTER TABLE `findBugs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `methodUID`
--

DROP TABLE IF EXISTS `methodUID`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `methodUID` (
  `methodUID` int(11) NOT NULL AUTO_INCREMENT,
  `ClassUID` int(11) DEFAULT NULL,
  `Method` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`methodUID`)
) ENGINE=MyISAM AUTO_INCREMENT=62 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `methodUID`
--

LOCK TABLES `methodUID` WRITE;
/*!40000 ALTER TABLE `methodUID` DISABLE KEYS */;

/*!40000 ALTER TABLE `methodUID` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reflection`
--

DROP TABLE IF EXISTS `reflection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `reflection` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `unityID` varchar(8) DEFAULT NULL,
  `date_added` datetime NOT NULL,
  `reviewed_unityID` varchar(8) DEFAULT NULL,
  `review` text,
  PRIMARY KEY (`id`),
  KEY `unityID` (`unityID`),
  KEY `reviewed_unityID` (`reviewed_unityID`)
) ENGINE=MyISAM AUTO_INCREMENT=57 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reflection`
--

LOCK TABLES `reflection` WRITE;
/*!40000 ALTER TABLE `reflection` DISABLE KEYS */;

/*!40000 ALTER TABLE `reflection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `testClassUID`
--

DROP TABLE IF EXISTS `testClassUID`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `testClassUID` (
  `testClassUID` int(11) NOT NULL AUTO_INCREMENT,
  `testClass` varchar(50) DEFAULT NULL,
  `testPackage` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`testClassUID`)
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `testClassUID`
--

LOCK TABLES `testClassUID` WRITE;
/*!40000 ALTER TABLE `testClassUID` DISABLE KEYS */;

/*!40000 ALTER TABLE `testClassUID` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `testMethodUID`
--

DROP TABLE IF EXISTS `testMethodUID`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `testMethodUID` (
  `testMethodUID` int(11) NOT NULL AUTO_INCREMENT,
  `testClassUID` int(11) NOT NULL,
  `testMethodName` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`testMethodUID`)
) ENGINE=MyISAM AUTO_INCREMENT=86 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `testMethodUID`
--

LOCK TABLES `testMethodUID` WRITE;
/*!40000 ALTER TABLE `testMethodUID` DISABLE KEYS */;

/*!40000 ALTER TABLE `testMethodUID` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `testTable`
--

DROP TABLE IF EXISTS `testTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `testTable` (
  `CommitUID` int(11) NOT NULL DEFAULT '0',
  `testMethodUID` int(11) DEFAULT NULL,
  `Passing` varchar(1) DEFAULT NULL,
  `Message` varchar(500) DEFAULT NULL,
  `Line` int(11) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `testTable`
--

LOCK TABLES `testTable` WRITE;
/*!40000 ALTER TABLE `testTable` DISABLE KEYS */;

/*!40000 ALTER TABLE `testTable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `unityID` varchar(8) DEFAULT NULL,
  `ProjectID` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=156 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;

/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-06-13 21:55:02
