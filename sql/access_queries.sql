-- MySQL dump 10.13  Distrib 5.7.22, for Linux (x86_64)
--
-- Host: localhost    Database: talentla_gestionale
-- ------------------------------------------------------
-- Server version	5.7.22-0ubuntu0.16.04.1

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
-- Table structure for table `access_queries`
--

DROP TABLE IF EXISTS `access_queries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `access_queries` (
  `Name` varchar(100) NOT NULL,
  `Query` varchar(2000) DEFAULT NULL,
  PRIMARY KEY (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `access_queries`
--

LOCK TABLES `access_queries` WRITE;
/*!40000 ALTER TABLE `access_queries` DISABLE KEYS */;
INSERT INTO `access_queries` VALUES ('ENTER_USER','INSERT INTO online_accesses (TalentCode, MemberType) VALUES (%s, %s)'),('EXISTS_ACCESS_CODE','SELECT AccessCode from (select AccessCode, IsActive FROM talentla_gestionale.talent_members union ALL select AccessCode, IsActive FROM talentla_gestionale.old_members_accesses WHERE IsActive = 1) R WHERE AccessCode = %s'),('EXISTS_TALENTCODE','SELECT TalentCode from (select TalentCode, IsActive FROM talentla_gestionale.talent_members union ALL select TalentCode, IsActive FROM talentla_gestionale.old_members_accesses WHERE IsActive = 1) R WHERE TalentCode = %s'),('EXIT_USER','DELETE FROM online_accesses WHERE TalentCode = %s'),('GET_ALL_INFO_ALARMS','SELECT Name, Token, Hostname, Port FROM list_alarms'),('GET_INFO_ALARM','SELECT Token, Hostname, Port FROM list_alarms WHERE Name = %s'),('GET_NEXT_ALARM_REQUEST','select Id, NameAlarm, AlarmAction from talentla_gestionale.list_request_alarms where isdone = 0 order by RequestaDate limit 1'),('GET_NEXT_REQUEST_ACCESS','select ID, AccessCode from talentla_gestionale.list_requests_accesses where IsDone = 0 order by AccessRequest asc limit 1'),('GET_NEXT_STRINGTOSEND','SELECT ID, StringToSend FROM talentla_gestionale.list_request_serials WHERE IsDone = 0 order by RequestDate limit 1'),('INFO_USER_ACCESS','Select R.Name, R.Surname, R.TalentCode, R.MemberType, R.DependingOn, R.AccessCode FROM (SELECT A.Name, A.Surname, A.TalentCode, A.MemberType, B.DependingOn, A.AccessCode FROM talentla_gestionale.talent_members A inner join talentla_gestionale.type_members B on A.MemberType = B.ID WHERE A.IsActive = 1 union ALL SELECT A.Name, A.Surname, A.TalentCode, A.MemberType, B.DependingOn, A.AccessCode FROM talentla_gestionale.old_members_accesses A inner join talentla_gestionale.type_members B on A.MemberType = B.ID WHERE A.IsActive = 1) R WHERE AccessCode = %s;'),('INSERT_ALARM_REQUEST','insert into talentla_gestionale.list_request_alarms (AlarmAction, NameAlarm) values(%s, %s)'),('INSERT_MEMBER_TABLE','insert into table_name (name, surname, MemberType, ReferenceZone, AccessCode, IsActive, TalentCode, Username, Password, FirstEmail, FiscalCode) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'),('INSERT_REQUEST_ACCESS','insert into talentla_gestionale.list_requests_accesses (AccessCode) values(%s)'),('INSERT_REQUEST_SERIAL','INSERT INTO talentla_gestionale.list_request_serials (StringToSend) values(%s)'),('IS_ONLINE_USER','SELECT * FROM online_accesses WHERE TalentCode = %s'),('LIST_MEMBER_DEPENDING','SELECT ID FROM type_members WHERE DependingOn = {0} OR DependingOn like \'{0},%%\' or DependingOn like \'%%,{0}\' or DependingOn like \'%%,{0},%%\''),('LOG_STATUS_REGISTER_ALARM','insert into log_status_alarms (Name, ErrorDescription, CodeError) VALUES (%s, %s, %s)'),('N_TYPE_USER','SELECT COUNT(ID) as N_MASTER FROM online_accesses WHERE MemberType in (%s)'),('N_USER_ONLINE','SELECT COUNT(ID) as N_MASTER FROM online_accesses'),('SAVE_LOG','INSERT INTO log_accesses (TalentCode, MemberType, AccessDate, IsEnter, AlarmActivation) VALUES (%s, %s, NOW(), %s, %s)'),('SET_ALARM_REQUEST_DONE','UPDATE talentla_gestionale.list_request_alarms set IsDone = 1 where id = %s'),('SET_REQUEST_DONE','update talentla_gestionale.list_requests_accesses set IsDone = 1 WHERE ID = %s'),('SET_REQUEST_SERIAL_DONE','update talentla_gestionale.list_request_serials set IsDone = 1 where id = %s'),('TRUNCATE_ONLINE_MEMBERS','TRUNCATE online_accesses'),('UPDATE_ACCESSCODE','update table_name set AccessCode = %s where TalentCode = %s');
/*!40000 ALTER TABLE `access_queries` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-06-02 18:50:24
