SELECT
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
			if_index_avg_scores I on M.ifIndex = I.ifIndex) T) Z;