/* ===== 1. Import ===== */
options validvarname=v7;

proc import datafile="/home/u64631998/bank/bank-additional-full.csv"
    out=work.bank_raw
    dbms=csv
    replace;
    delimiter=';';
    getnames=yes;
    guessingrows=max;
run;

/* ===== 2. Nettoyage ===== */
data work.bank_clean;
    set work.bank_raw;

    array txt{*} job marital education default housing loan;
    do i = 1 to dim(txt);
        if txt{i} = "unknown" then txt{i} = "";
    end;
    drop i;

    souscrit = (y = "yes");

    deja_contacte = (pdays ne 999);
    if pdays = 999 then pdays = .;

    length tranche_age $12;
    if age < 30 then tranche_age = "1. <30";
    else if age < 45 then tranche_age = "2. 30-44";
    else if age < 60 then tranche_age = "3. 45-59";
    else tranche_age = "4. 60+";
run;

/* ===== 3. Indicateurs ===== */
proc sql;
    create table work.kpi_metier as
    select job,
           count(*)       as nb_clients,
           sum(souscrit)  as nb_souscriptions,
           mean(souscrit) as taux_souscription format=percent8.1,
           mean(campaign) as nb_appels_moyen format=8.1
    from work.bank_clean
    where job ne ""
    group by job
    order by taux_souscription desc;
quit;

proc sql;
    create table work.kpi_contact as
    select deja_contacte,
           count(*)       as nb_clients,
           mean(souscrit) as taux_souscription format=percent8.1
    from work.bank_clean
    group by deja_contacte;
quit;

/* ===== 4. Export sans les formats d'affichage ===== */
data work.kpi_metier_export;
    set work.kpi_metier;
    format taux_souscription nb_appels_moyen;
run;

data work.kpi_contact_export;
    set work.kpi_contact;
    format taux_souscription;
run;

proc export data=work.kpi_metier_export
    outfile="/home/u64631998/bank/sas_kpi_metier.csv"
    dbms=csv replace;
run;

proc export data=work.kpi_contact_export
    outfile="/home/u64631998/bank/sas_kpi_contact.csv"
    dbms=csv replace;
run;