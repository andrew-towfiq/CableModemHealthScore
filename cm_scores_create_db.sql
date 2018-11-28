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
        SNR_SCORE(`snr_pl_h`.`snr`, 40) AS `snr_score`,
        PL_SCORE(`snr_pl_h`.`direction`,
                `snr_pl_h`.`pl`,
                0) AS `pl_score`
    FROM
        `snr_pl_h`;
        
        
CREATE DEFINER=`andrew`@`%` FUNCTION `SNR_SCORE`(snr float, target float) RETURNS float
return (100.0*snr/target)

CREATE DEFINER=`andrew`@`%` FUNCTION `pl_target`(direction int) RETURNS float
return if(direction = 1, 45, 0)

delimiter //
CREATE DEFINER=`andrew`@`%` FUNCTION `PL_SCORE`(direction int, pl float, threshold float) RETURNS float
begin
  declare delta float;
  set delta = abs(pl-pl_target(direction));
  
  if (delta < threshold) then
    return 100.0;
  else
    return 100.0 / (delta+1);
  end if;
  
end //
delimiter ;        