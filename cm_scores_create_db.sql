
-- drop table if exists snr_pl_h;
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
    
-- drop view if exists v_c_snr_pl_scores;
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `andrew`@`%` 
    SQL SECURITY DEFINER
VIEW `v_c_snr_pl_scores` AS
    SELECT 
        `snr_pl_c`.`id` AS `id`,
        `snr_pl_c`.`ts` AS `ts`,
        `snr_pl_c`.`mac` AS `mac`,
        `snr_pl_c`.`direction` AS `direction`,
        `snr_pl_c`.`ifIndex` AS `ifIndex`,
        `snr_pl_c`.`snr` AS `snr`,
        `snr_pl_c`.`pl` AS `pl`,
        snr_score(`snr_pl_c`.`snr`, 33) AS `snr_score`,
        pl_score(`snr_pl_c`.`direction`,
                `snr_pl_c`.`pl`)
                AS `pl_score`
    FROM
        `snr_pl_c`;

-- drop table latest_mac_if_poll;
CREATE TABLE latest_mac_if_poll AS
	(SELECT 
		MAX(id) id, mac, ifIndex, direction, MAX(ts) ts, snr, snr_score, pl, pl_score 
	FROM v_c_snr_pl_scores 
	GROUP BY mac, ifIndex);

-- drop table if_index_avg_scores;
CREATE TABLE if_index_avg_scores AS 
SELECT 
    a.ifIndex, MAX(ts) ts, COUNT(id) cnt, 
    AVG(snr_score) avg_snr_score, 
    AVG(pl_score) avg_pl_score,
    STDDEV(snr_score) as stddev_snr_score,
    STDDEV(pl_score) as stddev_pl_score
  FROM 
    (SELECT * FROM latest_mac_if_poll) a 
  GROUP BY ifIndex;
  
-- drop table if exists cm_health_scores;
CREATE TABLE cm_health_scores AS 
(SELECT
	mac, ifIndex, direction, cm_snr, cm_pl,
    (log10_snr_health + log10_pl_health)/2 as avg_log_health,
    (.8 * log10_snr_health + .2 * log10_pl_health) as w_avg_log_health,
    (stddev_snr_health + stddev_pl_health)/2 as avg_stddev_health,
    (.8*stddev_snr_health + .2*stddev_pl_health) as w_avg_stddev_health
FROM
	(SELECT
		mac, ifIndex, direction, cm_snr, cm_pl,
		10*log10(snr_score_ratio) as log10_snr_health,
		10*log10(pl_score_ratio) as log10_pl_health,
		(cm_snr_score-if_snr_score)/stddev_snr_score as stddev_snr_health,
		(cm_pl_score-if_pl_score)/stddev_pl_score as stddev_pl_health
	FROM
		(SELECT
			M.mac, M.ifIndex, M.direction, M.snr as cm_snr, M.pl as cm_pl, M.snr_score as cm_snr_score, M.pl_score as cm_pl_score,
			I.avg_snr_score as if_snr_score, I.avg_pl_score as if_pl_score,
			I.stddev_snr_score,
			I.stddev_pl_score,
			snr_score/I.avg_snr_score as snr_score_ratio,
			pl_score/I.avg_pl_score as pl_score_ratio
		FROM 
			latest_mac_if_poll M
		JOIN
			if_index_avg_scores I on M.ifIndex = I.ifIndex) T) Z);

-- drop function if exists snr_score;
delimiter // 
CREATE DEFINER=`andrew`@`%` FUNCTION `snr_score`(snr float, target float) RETURNS float
RETURN (100.0 * (1 / (1 + EXP(-1 * snr + target))));
//
delimiter ;
     
-- drop function if exists `pl_target`;
CREATE DEFINER=`andrew`@`%` FUNCTION `pl_target`(direction int) RETURNS float
RETURN if(direction = 1, 40, 0);


-- drop function if exists `pl_score`;
delimiter // 
CREATE DEFINER=`andrew`@`%` FUNCTION `pl_score`(direction int, pl float) RETURNS float
BEGIN
	DECLARE ret_score float;
	IF direction = 1 THEN
		SET ret_score = (100.0 * EXP(-1 * POW((1/12) * (pl - 40), 10))) ;
	ELSEIF direction = 2 THEN
		SET ret_score =  (100.0 * EXP(-1 * POW((1/15) * (pl - 0), 6))) ;
	end if;
    RETURN ret_score;
END //

delimiter ;
