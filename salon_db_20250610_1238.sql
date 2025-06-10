-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: salon_db
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer` (
  `cust_num` int NOT NULL AUTO_INCREMENT,
  `cust_phone` varchar(20) NOT NULL,
  `cust_address` varchar(45) NOT NULL,
  `cust_name` varchar(20) NOT NULL,
  PRIMARY KEY (`cust_num`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer`
--

LOCK TABLES `customer` WRITE;
/*!40000 ALTER TABLE `customer` DISABLE KEYS */;
/*!40000 ALTER TABLE `customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order`
--

DROP TABLE IF EXISTS `order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order` (
  `order_num` int NOT NULL AUTO_INCREMENT,
  `order_date` date NOT NULL,
  `amount` int NOT NULL,
  `agent` int NOT NULL,
  `customer` int NOT NULL,
  PRIMARY KEY (`order_num`),
  KEY `customer_idx` (`customer`),
  KEY `agent_idx` (`agent`),
  CONSTRAINT `order_agent` FOREIGN KEY (`agent`) REFERENCES `user` (`user_num`),
  CONSTRAINT `order_customer` FOREIGN KEY (`customer`) REFERENCES `customer` (`cust_num`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order`
--

LOCK TABLES `order` WRITE;
/*!40000 ALTER TABLE `order` DISABLE KEYS */;
/*!40000 ALTER TABLE `order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_receipt`
--

DROP TABLE IF EXISTS `order_receipt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_receipt` (
  `order_num` int NOT NULL,
  `product_num` int NOT NULL,
  `quantity` int NOT NULL,
  `price` int NOT NULL,
  `sum` int NOT NULL,
  PRIMARY KEY (`order_num`,`product_num`),
  KEY `product_idx` (`product_num`),
  CONSTRAINT `order` FOREIGN KEY (`order_num`) REFERENCES `order` (`order_num`),
  CONSTRAINT `ordered_product` FOREIGN KEY (`product_num`) REFERENCES `product` (`product_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_receipt`
--

LOCK TABLES `order_receipt` WRITE;
/*!40000 ALTER TABLE `order_receipt` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_receipt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product`
--

DROP TABLE IF EXISTS `product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product` (
  `product_num` int NOT NULL AUTO_INCREMENT,
  `product_name` varchar(15) NOT NULL,
  `price` int NOT NULL,
  `cost` int NOT NULL,
  `supplier` int NOT NULL,
  `safe_stock` int NOT NULL DEFAULT '50',
  PRIMARY KEY (`product_num`),
  KEY `supplier_idx` (`supplier`),
  CONSTRAINT `product_supplier` FOREIGN KEY (`supplier`) REFERENCES `supplier` (`sup_num`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product`
--

LOCK TABLES `product` WRITE;
/*!40000 ALTER TABLE `product` DISABLE KEYS */;
/*!40000 ALTER TABLE `product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase`
--

DROP TABLE IF EXISTS `purchase`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase` (
  `purchase_num` int NOT NULL AUTO_INCREMENT,
  `purchase_date` date NOT NULL,
  `purchase_amount` int NOT NULL,
  `agent` int NOT NULL,
  PRIMARY KEY (`purchase_num`),
  KEY `agent_idx` (`agent`),
  CONSTRAINT `purchase_agent` FOREIGN KEY (`agent`) REFERENCES `user` (`user_num`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase`
--

LOCK TABLES `purchase` WRITE;
/*!40000 ALTER TABLE `purchase` DISABLE KEYS */;
/*!40000 ALTER TABLE `purchase` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_receipt`
--

DROP TABLE IF EXISTS `purchase_receipt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_receipt` (
  `purchase_number` int NOT NULL,
  `product_num` int NOT NULL,
  `quantity` int NOT NULL,
  `cost` int NOT NULL,
  `sum` int NOT NULL,
  PRIMARY KEY (`purchase_number`,`product_num`),
  KEY `purchased_product_idx` (`product_num`),
  CONSTRAINT `purchase` FOREIGN KEY (`purchase_number`) REFERENCES `purchase` (`purchase_num`),
  CONSTRAINT `purchased_product` FOREIGN KEY (`product_num`) REFERENCES `product` (`product_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_receipt`
--

LOCK TABLES `purchase_receipt` WRITE;
/*!40000 ALTER TABLE `purchase_receipt` DISABLE KEYS */;
/*!40000 ALTER TABLE `purchase_receipt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `stock_view`
--

DROP TABLE IF EXISTS `stock_view`;
/*!50001 DROP VIEW IF EXISTS `stock_view`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `stock_view` AS SELECT 
 1 AS `product_num`,
 1 AS `product_name`,
 1 AS `total_purchase`,
 1 AS `total_sales`,
 1 AS `stock_quantity`,
 1 AS `stock_value`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `supplier`
--

DROP TABLE IF EXISTS `supplier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `supplier` (
  `sup_num` int NOT NULL AUTO_INCREMENT,
  `sup_com` varchar(25) NOT NULL,
  `sup_address` varchar(45) NOT NULL,
  `sup_name` varchar(25) NOT NULL,
  `sup_phone` varchar(20) NOT NULL,
  PRIMARY KEY (`sup_num`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `supplier`
--

LOCK TABLES `supplier` WRITE;
/*!40000 ALTER TABLE `supplier` DISABLE KEYS */;
/*!40000 ALTER TABLE `supplier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `user_num` int NOT NULL AUTO_INCREMENT,
  `user_accont` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL,
  `name` varchar(15) NOT NULL,
  `user_type` varchar(5) NOT NULL DEFAULT 'agent',
  PRIMARY KEY (`user_num`),
  UNIQUE KEY `user_accont_UNIQUE` (`user_accont`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (3,'kumurato71','0000','Kumura','agent'),(4,'ricky_t_71','0000','Richard','admin'),(5,'admin','00000000','sys_admin','admin'),(6,'A001','00000000','user01','agent');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Final view structure for view `stock_view`
--

/*!50001 DROP VIEW IF EXISTS `stock_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `stock_view` AS select `p`.`product_num` AS `product_num`,`p`.`product_name` AS `product_name`,ifnull(sum(`pr_in`.`quantity`),0) AS `total_purchase`,ifnull(sum(`or_out`.`quantity`),0) AS `total_sales`,(ifnull(sum(`pr_in`.`quantity`),0) - ifnull(sum(`or_out`.`quantity`),0)) AS `stock_quantity`,((ifnull(sum(`pr_in`.`quantity`),0) - ifnull(sum(`or_out`.`quantity`),0)) * `p`.`cost`) AS `stock_value` from ((`product` `p` left join `purchase_receipt` `pr_in` on((`p`.`product_num` = `pr_in`.`product_num`))) left join `order_receipt` `or_out` on((`p`.`product_num` = `or_out`.`product_num`))) group by `p`.`product_num`,`p`.`product_name`,`p`.`cost` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-10 12:39:18
