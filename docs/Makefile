data: \
	us_ofac \
	eu_meps \
	us_bis_denied \
	un_sc_sanctions \
	everypolitician \
	gb_hmt_sanctions \
	ch_seco_sanctions \
	ua_sdfm_blacklist \
	eu_eeas_sanctions \
	au_dfat_sanctions \
	us_cia_world_leaders \
	ca_dfatd_sema_sanctions

us_ofac: us_ofac.occrp-data-export

eu_meps: eu_meps.occrp-data-export

everypolitician: everypolitician.occrp-data-export

us_cia_world_leaders: us_cia_world_leaders.occrp-data-export

un_sc_sanctions: un_sc_sanctions.occrp-data-export

ch_seco_sanctions: ch_seco_sanctions.occrp-data-export

ua_sdfm_blacklist: ua_sdfm_blacklist.occrp-data-export

us_bis_denied: us_bis_denied.occrp-data-export

gb_hmt_sanctions: gb_hmt_sanctions.occrp-data-export

eu_eeas_sanctions: eu_eeas_sanctions.occrp-data-export

au_dfat_sanctions: au_dfat_sanctions.occrp-data-export

ca_dfatd_sema_sanctions: ca_dfatd_sema_sanctions.occrp-data-export

%.occrp-data-export:
	curl -o $*.json -s https://storage.googleapis.com/occrp-data-exports/$*/$*.json
