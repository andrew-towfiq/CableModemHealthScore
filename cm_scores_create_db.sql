show create table snr_pl_h;

drop table if exists snr_pl_h;
CREATE TABLE `snr_pl_h` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `ts` datetime DEFAULT NULL,
  `mac` char(12) DEFAULT NULL,
  `direction` tinyint(4) DEFAULT NULL,
  `ifIndex` int(11) DEFAULT NULL,
  `snr` float DEFAULT NULL,
  `pl` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_mac` (`mac`),
  KEY `idx_direction` (`direction`),
  KEY `idx_ifIndex` (`ifIndex`)
) ;

drop view if exists v_snr_pl_scores;
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `andrew`@`%` 
    SQL SECURITY DEFINER
VIEW `v_snr_pl_scores` AS
    SELECT 
        `snr_pl_h`.`id` AS `id`,
        `snr_pl_h`.`ts` AS `ts`,
        `snr_pl_h`.`mac` AS `mac`,
        `snr_pl_h`.`direction` AS `direction`,
        `snr_pl_h`.`ifIndex` AS `ifIndex`,
        `snr_pl_h`.`snr` AS `snr`,
        `snr_pl_h`.`pl` AS `pl`,
        snr_score(`snr_pl_h`.`snr`, 40) AS `snr_score`,
        pl_score(`snr_pl_h`.`direction`,
                `snr_pl_h`.`pl`)
                AS `pl_score`
    FROM
        `snr_pl_h`;
        


drop function if exists snr_score;
delimiter // 
CREATE DEFINER=`andrew`@`%` FUNCTION `snr_score`(snr float, target float) RETURNS float
return(100.0 * 1 / (1 + EXP(-1 * (snr - (target - 7)))))
//
delimiter ;
     
drop function if exists `pl_target`;
CREATE DEFINER=`andrew`@`%` FUNCTION `pl_target`(direction int) RETURNS float
return if(direction = 1, 45, 0);

drop function if exists `pl_score`;
CREATE DEFINER=`andrew`@`%` FUNCTION `pl_score`(direction int, pl float) RETURNS float
return (100.0 * EXP(-1 * POW((1/6) * (pl - pl_target(direction)), 6)));
