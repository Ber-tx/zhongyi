-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: zhongyi
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(100) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (2,'admin','$2a$10$kwoN8lZvPltdI76V4ETWBOhTV8v6F43w/rQzt.edFERtgwOeyi7Ce','2026-03-23 00:42:49');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `diagnosis`
--

DROP TABLE IF EXISTS `diagnosis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `diagnosis` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `patient_id` bigint NOT NULL COMMENT '关联患者ID',
  `wen_scores` text COMMENT '问诊9种体质得分(JSON格式)',
  `wen_conclusion` varchar(50) DEFAULT NULL COMMENT '问诊初步体质结论',
  `wang_image_url` varchar(255) DEFAULT NULL COMMENT '面色/舌象照片路径',
  `wang_result` text COMMENT '视觉分析结果',
  `status` int DEFAULT '0' COMMENT '诊断状态: 0-进行中, 1-已完成',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `qie_heart_rate` double DEFAULT NULL COMMENT '平均心率',
  `qie_spo2` double DEFAULT NULL COMMENT '平均血氧',
  `qie_valid_rate` decimal(5,2) DEFAULT NULL COMMENT '信号有效率（0-100）',
  `qie_sample_count` int DEFAULT NULL COMMENT '有效采样次数',
  `qie_tcm_suggestion` text COMMENT '中医建议（Python生成）',
  `wen_audio_conclusion` varchar(255) DEFAULT NULL COMMENT '声诊结论',
  `wen_audio_features` text COMMENT '音频特征(JSON)',
  `wen_audio_confidence` double DEFAULT NULL COMMENT 'AI识别置信度',
  `wen_audio_tags` varchar(255) DEFAULT NULL COMMENT '体质标签',
  `wen_audio_url` varchar(500) DEFAULT NULL COMMENT '闻诊音频地址',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='中医诊断记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `diagnosis`
--

LOCK TABLES `diagnosis` WRITE;
/*!40000 ALTER TABLE `diagnosis` DISABLE KEYS */;
INSERT INTO `diagnosis` VALUES (1,1,'{\"yx0\":12,\"xyy\":11,\"yx1\":10,\"qt\":9,\"ss\":13,\"tx\":12,\"zy\":11}','平和质','/upload/wang/1.jpg','面色红润，舌苔薄白，整体平和',0,'2026-01-01 09:01:00','2026-01-01 09:05:00',72,98,100.00,30,'脉象和缓，节律均匀，气血平和','语声平稳，气息均匀','{\"mfcc1\":85,\"mfcc2\":72}',0.92,'[\"平和\",\"气血充足\"]','/audio/1.wav'),(2,2,'{\"yx0\":14,\"xyy\":13,\"yx1\":12,\"qt\":8,\"ss\":10,\"tx\":9,\"zy\":11}','气郁质','/upload/wang/2.jpg','面色偏青，情绪不畅，肝气不舒',0,'2026-01-01 09:11:00','2026-01-01 09:15:00',78,97,99.00,32,'脉象偏弦，肝郁气滞，宜疏肝理气','语声偏闷，叹气较多','{\"mfcc1\":92,\"mfcc2\":78}',0.85,'[\"气郁\",\"肝郁\"]','/audio/2.wav'),(3,3,'{\"yx0\":9,\"xyy\":8,\"yx1\":7,\"qt\":14,\"ss\":13,\"tx\":12,\"zy\":11}','气虚质','/upload/wang/3.jpg','面色淡白，易疲劳，语声低微',0,'2026-01-01 09:21:00','2026-01-01 09:25:00',68,96,100.00,28,'脉象虚弱，中气不足，宜补气健脾','语声低微，气短懒言','{\"mfcc1\":78,\"mfcc2\":65}',0.88,'[\"气虚\",\"乏力\"]','/audio/3.wav'),(4,4,'{\"yx0\":13,\"xyy\":12,\"yx1\":11,\"qt\":10,\"ss\":9,\"tx\":8,\"zy\":14}','痰湿质','/upload/wang/4.jpg','舌苔厚腻，体型偏胖，痰湿内停',0,'2026-01-01 09:31:00','2026-01-01 09:35:00',74,97,98.50,35,'脉象滑利，痰湿内阻，宜健脾祛湿','痰多声浊，呼吸偏沉','{\"mfcc1\":95,\"mfcc2\":80}',0.86,'[\"痰湿\",\"脾虚\"]','/audio/4.wav'),(5,5,'{\"yx0\":11,\"xyy\":10,\"yx1\":14,\"qt\":13,\"ss\":12,\"tx\":11,\"zy\":9}','湿热质','/upload/wang/5.jpg','面油长痘，口苦口臭，湿热内蕴',0,'2026-01-01 09:41:00','2026-01-01 09:45:00',76,98,100.00,33,'脉象滑数，湿热并重，宜清热利湿','语声偏燥，口气偏重','{\"mfcc1\":90,\"mfcc2\":82}',0.84,'[\"湿热\",\"上火\"]','/audio/5.wav'),(6,6,'{\"yx0\":15,\"xyy\":14,\"yx1\":13,\"qt\":9,\"ss\":8,\"tx\":7,\"zy\":10}','血瘀质','/upload/wang/6.jpg','面色晦暗，唇色偏紫，气血瘀滞',0,'2026-01-01 09:51:00','2026-01-01 09:55:00',80,97,99.20,31,'脉象涩滞，瘀血内阻，宜活血化瘀','语声偏紧，气息不畅','{\"mfcc1\":98,\"mfcc2\":85}',0.83,'[\"血瘀\",\"气滞\"]','/audio/6.wav'),(7,7,'{\"yx0\":8,\"xyy\":9,\"yx1\":10,\"qt\":11,\"ss\":12,\"tx\":13,\"zy\":15}','阳虚质','/upload/wang/7.jpg','畏寒怕冷，手脚冰凉，阳气不足',0,'2026-01-01 10:01:00','2026-01-01 10:05:00',65,96,100.00,29,'脉象沉迟，阳虚寒盛，宜温阳散寒','语声偏低，畏寒喜暖','{\"mfcc1\":72,\"mfcc2\":60}',0.89,'[\"阳虚\",\"怕冷\"]','/audio/7.wav'),(8,8,'{\"yx0\":10,\"xyy\":12,\"yx1\":11,\"qt\":15,\"ss\":14,\"tx\":13,\"zy\":8}','阴虚质','/upload/wang/8.jpg','口干咽燥，手足心热，阴虚火旺',0,'2026-01-01 10:11:00','2026-01-01 10:15:00',75,98,98.80,34,'脉象细数，阴液不足，宜滋阴降火','语声偏细，口干少津','{\"mfcc1\":88,\"mfcc2\":76}',0.87,'[\"阴虚\",\"内热\"]','/audio/8.wav'),(9,9,'{\"yx0\":12,\"xyy\":11,\"yx1\":10,\"qt\":9,\"ss\":8,\"tx\":14,\"zy\":13}','特禀质','/upload/wang/9.jpg','易过敏，皮肤敏感，体质特异',0,'2026-01-01 10:21:00','2026-01-01 10:25:00',73,97,100.00,30,'脉象偏浮，卫气不固，宜固表抗过敏','语声清浅，易喷嚏咳嗽','{\"mfcc1\":86,\"mfcc2\":74}',0.82,'[\"过敏\",\"特禀\"]','/audio/9.wav'),(10,10,'{\"yx0\":11,\"xyy\":13,\"yx1\":12,\"qt\":10,\"ss\":9,\"tx\":8,\"zy\":11}','气郁质','/upload/wang/10.jpg','情绪焦虑，胸闷不舒，肝气郁结',0,'2026-01-01 10:31:00','2026-01-01 10:35:00',79,97,99.10,32,'脉象弦细，情志不舒，宜疏肝解郁','语声压抑，多叹气','{\"mfcc1\":91,\"mfcc2\":79}',0.85,'[\"气郁\",\"焦虑\"]','/audio/10.wav'),(11,11,'{\"yx0\":9,\"xyy\":8,\"yx1\":7,\"qt\":12,\"ss\":11,\"tx\":10,\"zy\":13}','气虚质','/upload/wang/11.jpg','易出汗，易疲劳，中气虚弱',0,'2026-01-01 10:41:00','2026-01-01 10:45:00',67,96,100.00,27,'脉象虚弱，气虚自汗，宜益气固表','语声无力，易喘','{\"mfcc1\":75,\"mfcc2\":63}',0.88,'[\"气虚\",\"自汗\"]','/audio/11.wav'),(12,12,'{\"yx0\":13,\"xyy\":12,\"yx1\":11,\"qt\":10,\"ss\":9,\"tx\":14,\"zy\":8}','痰湿质','/upload/wang/12.jpg','身体困重，腹胀便黏，痰湿偏盛',0,'2026-01-01 10:51:00','2026-01-01 10:55:00',74,97,98.60,35,'脉象濡滑，脾虚湿盛，宜化痰祛湿','痰多声重，身体困重','{\"mfcc1\":94,\"mfcc2\":81}',0.86,'[\"痰湿\",\"困重\"]','/audio/12.wav'),(13,13,'{\"yx0\":14,\"xyy\":13,\"yx1\":12,\"qt\":8,\"ss\":7,\"tx\":9,\"zy\":11}','血瘀质','/upload/wang/13.jpg','身体偶有刺痛，面色偏暗，瘀血阻滞',0,'2026-01-01 11:01:00','2026-01-01 11:05:00',81,97,99.30,31,'脉象涩紧，经络瘀阻，宜活血通络','语声偏沉，偶有胸闷','{\"mfcc1\":97,\"mfcc2\":84}',0.83,'[\"血瘀\",\"刺痛\"]','/audio/13.wav'),(14,14,'{\"yx0\":10,\"xyy\":11,\"yx1\":15,\"qt\":14,\"ss\":13,\"tx\":12,\"zy\":9}','湿热质','/upload/wang/14.jpg','口苦心烦，大便黏滞，湿热下注',0,'2026-01-01 11:11:00','2026-01-01 11:15:00',77,98,100.00,33,'脉象滑数，湿热郁蒸，宜清热化湿','语声偏燥，口苦','{\"mfcc1\":89,\"mfcc2\":83}',0.84,'[\"湿热\",\"口苦\"]','/audio/14.wav'),(15,15,'{\"yx0\":11,\"xyy\":10,\"yx1\":9,\"qt\":11,\"ss\":12,\"tx\":13,\"zy\":14}','平和质','/upload/wang/15.jpg','面色正常，精神尚可，体质平和',0,'2026-01-01 11:21:00','2026-01-01 11:25:00',71,98,100.00,30,'脉象和缓，气血调和，作息规律即可','语声清晰，气息平稳','{\"mfcc1\":84,\"mfcc2\":71}',0.93,'[\"平和\",\"健康\"]','/audio/15.wav'),(16,16,NULL,NULL,NULL,NULL,0,'2026-03-23 23:10:28','2026-03-23 23:10:28',NULL,NULL,NULL,NULL,NULL,'气滞血瘀','{\"mfcc_std_1\":69.1276626586914,\"voiced_ratio\":0.3807531380753138,\"f0_mean\":938.091820548078,\"mfcc_mean_10\":2.0597245693206787,\"rms_energy\":0.06755079329013824,\"mfcc_mean_13\":-1.0262444019317627,\"mfcc_mean_11\":-5.839970588684082,\"mfcc_mean_12\":1.237388014793396,\"duration\":7.62,\"mfcc_mean_7\":-11.945189476013184,\"mfcc_std_7\":17.410860061645508,\"crest_factor\":14.803675128203459,\"mfcc_mean_6\":10.253498077392578,\"mfcc_std_6\":11.960957527160645,\"mfcc_mean_5\":-8.16944694519043,\"mfcc_std_9\":10.500771522521973,\"mfcc_mean_4\":-1.2840622663497925,\"mfcc_std_8\":20.954164505004883,\"mfcc_std_3\":16.3050594329834,\"mfcc_std_2\":34.575416564941406,\"mfcc_std_5\":15.614095687866211,\"mfcc_mean_9\":-9.388142585754395,\"shimmer\":0.20673703346155362,\"mfcc_std_4\":24.441720962524414,\"mfcc_mean_8\":-15.889169692993164,\"mfcc_mean_3\":-22.130878448486328,\"mfcc_mean_2\":43.02727127075195,\"mfcc_mean_1\":-191.8735809326172,\"mfcc_std_13\":9.563092231750488,\"mfcc_std_10\":10.887140274047852,\"hnr\":4.571985915058951,\"mfcc_std_12\":9.109128952026367,\"mfcc_std_11\":8.265417098999023,\"f0_std\":467.4975000756724,\"jitter\":0.05227550755108234}',0.8250000000000002,'[\"气机不畅\",\"音调波动\",\"声音不连贯\"]','E:\\项目\\zhongyi_uploads\\audio\\4e6a397f-83d7-4f9a-b19f-92efcc72ef1d.webm');
/*!40000 ALTER TABLE `diagnosis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patients`
--

DROP TABLE IF EXISTS `patients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patients` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `birthday` date DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `id_card` varchar(20) NOT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_card` (`id_card`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patients`
--

LOCK TABLES `patients` WRITE;
/*!40000 ALTER TABLE `patients` DISABLE KEYS */;
INSERT INTO `patients` VALUES (1,'陈一','男','1992-03-12','北京市海淀区中关村大街1号','110108199203121234','2026-01-01 09:00:00'),(2,'刘二','女','1988-07-24','上海市浦东新区张江路2号','310115198807245678','2026-01-01 09:10:00'),(3,'张三','男','1995-11-05','广州市天河区天河路3号','440106199511059012','2026-01-01 09:20:00'),(4,'李四','女','1990-01-18','深圳市南山区科技园4号','440305199001182345','2026-01-01 09:30:00'),(5,'王五','男','1985-09-30','杭州市西湖区文二路5号','330106198509306789','2026-01-01 09:40:00'),(6,'赵六','女','1998-04-07','南京市玄武区中山路6号','320102199804071357','2026-01-01 09:50:00'),(7,'孙七','男','1993-06-21','成都市高新区天府大道7号','510107199306212468','2026-01-01 10:00:00'),(8,'周八','女','1987-12-03','武汉市洪山区珞喻路8号','420111198712033579','2026-01-01 10:10:00'),(9,'吴九','男','1991-08-15','西安市雁塔区高新路9号','610113199108154680','2026-01-01 10:20:00'),(10,'郑十','女','1996-02-28','重庆市渝北区金开大道10号','500112199602285791','2026-01-01 10:30:00'),(11,'冯十一','男','1989-05-09','天津市南开区卫津路11号','120104198905096802','2026-01-01 10:40:00'),(12,'陈十二','女','1994-10-17','苏州市工业园区星湖街12号','320503199410177913','2026-01-01 10:50:00'),(13,'杨十三','男','1986-04-22','郑州市金水区花园路13号','410105198604228024','2026-01-01 11:00:00'),(14,'黄十四','女','1997-07-04','长沙市岳麓区麓山南路14号','430104199707049135','2026-01-01 11:10:00'),(15,'罗十五','男','1990-12-11','合肥市蜀山区长江西路15号','340104199012110246','2026-01-01 11:20:00'),(16,'张三丰','男','1980-05-15','湖北省武当山特区太极路1号','420301198005153219','2026-03-23 23:10:13');
/*!40000 ALTER TABLE `patients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `question`
--

DROP TABLE IF EXISTS `question`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `question` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `content` varchar(255) NOT NULL COMMENT '问题内容(如:您容易疲乏吗?)',
  `sort` int DEFAULT '0' COMMENT '题目排序',
  `audio_url` varchar(255) DEFAULT NULL COMMENT '对应音频文件的路径（如：/audio/q1.mp3）',
  `is_reverse` tinyint(1) DEFAULT '0' COMMENT '是否为反向计分题（仅针对平和质判断）',
  `constitution_codes` varchar(100) DEFAULT NULL COMMENT '关联体质标识，用逗号分隔（如：ph,qx 代表同时影响平和质和气虚质）',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='题库表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `question`
--

LOCK TABLES `question` WRITE;
/*!40000 ALTER TABLE `question` DISABLE KEYS */;
INSERT INTO `question` VALUES (1,'您精力充沛吗？（指精神头足，乐于做事）',1,NULL,0,'ph'),(2,'您容易疲乏吗？（指体力如何，动一下就累）',2,NULL,0,'qx'),(3,'您容易气短（呼吸短促，接不上气）吗？',3,NULL,0,'qx'),(4,'您说话声音低弱无力吗？（指说话没有力气）',4,NULL,0,'qx'),(5,'您感到闷闷不乐、情绪低沉吗？（指心情不愉快，情绪低落）',5,NULL,0,'qy'),(6,'您容易精神紧张、焦虑不安吗？（指遇事是否容易紧张）',6,NULL,0,'qy'),(7,'您因为生活状态改变而感到孤独、失落吗？',7,NULL,0,'qy'),(8,'您容易感到害怕或受到惊吓吗？',8,NULL,0,'qy'),(9,'您感到身体超重不轻松吗？（系统将通过身高体重自动计算BMI指数）',9,NULL,0,'ts'),(10,'您眼睛干涩吗？',10,NULL,0,'yx0'),(11,'您手脚发凉吗？（不包含因周围温度改变或穿的少导致的手脚发凉）',11,NULL,0,'yx1'),(12,'您胃脘部、背部或腰膝部怕冷吗？',12,NULL,0,'yx1'),(13,'您比一般人耐受不了寒冷吗？（指比别人更害怕冬天或者夏天的空调、电扇等）',13,NULL,0,'yx1'),(14,'您容易患感冒吗？（指1年内感冒次数）',14,NULL,0,'qx'),(15,'您没有感冒时也会鼻塞、流鼻涕吗？',15,NULL,0,'tb'),(16,'您有口粘口腻，或睡眠打鼾吗？',16,NULL,0,'ts'),(17,'您过敏的频率是？（药物、食物、花粉等）',17,NULL,0,'tb'),(18,'您的皮肤容易起荨麻疹吗？（包括风团、风疹块、风疙瘩）',18,NULL,0,'tb'),(19,'您皮肤在不知不觉间出现青紫瘀斑（皮下出血）吗？（指皮肤没有在外伤的情况下出现）',19,NULL,0,'xy'),(20,'您的皮肤一抓就红，并出现抓痕吗？（指被指甲或者钝物划过的反应）',20,NULL,0,'tb'),(21,'您皮肤或口唇干燥吗？',21,NULL,0,'yx0'),(22,'您有肢体麻木或固定部位疼痛的感觉吗？',22,NULL,0,'xy'),(23,'您面部或鼻部有油腻或者油亮发光吗？（指脸上或鼻子）',23,NULL,0,'sr'),(24,'您面色晦暗或目眶晦暗，或出现褐色斑块/斑点吗？',24,NULL,0,'xy'),(25,'您有皮肤湿疹、疮疖吗？',25,NULL,0,'sr'),(26,'您感到口干咽燥、总想喝水吗？',26,NULL,0,'yx0'),(27,'您感到口苦或嘴里有异味吗？（指口臭或口苦）',27,NULL,0,'sr'),(28,'您腹部肥大吗？（腹部脂肪肥厚）',28,NULL,0,'ts'),(29,'您吃(喝)凉的东西会感到不舒服或者怕吃(喝)凉的东西吗？',29,NULL,0,'yx1'),(30,'您有大便粘滞不爽或解不尽的感觉吗？',30,NULL,0,'sr'),(31,'您容易大便干燥吗？',31,NULL,0,'yx0'),(32,'您舌苔厚腻或有舌苔厚厚的感觉吗？（如果自我感觉不清楚可由调查员观察后填写）',32,NULL,0,'ts'),(33,'您舌下脉络瘀紫或增粗吗？（可由调查员观察后填写）',33,NULL,0,'xy');
/*!40000 ALTER TABLE `question` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-24  1:25:12
