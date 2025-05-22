def flatten_dict_to_list(d):
    """
    Flatten a dictionary into a list of its keys and values.

    Args:
        d (dict): The dictionary to flatten.

    Returns:
        list: A flattened list containing keys and values.
    """
    return [item for key, values in d.items() for item in [key] + values]

HEMOSTATIC_DEVICES = {
    "Hemoblast": ["Biom'up"],
    "Hemoblast Bellows": ["Bellows applicator"],
    "Gelfoam": ["Gelatin sponge"],
    "Gelfoam Plus": ["Hemostatic kit"],
    "Surgifoam": ["Gelatin powder", "Ethicon gelatin"],
    "Avitene": ["Microfibrillar Collagen", "MCH", "Davol"],
    "Ultrafoam": ["Bard collagen"],
    "Helistat": ["Integra sponge"],
    "Helitene": ["Absorbable felt", "Integra felt"],
    "Instat": ["Microfibrillar"],
    "Surgicel": ["Oxidized cellulose", "ORC", "Fibrillar", "Nu-Knit"],
    "Arista": ["Plant-based powder", "BD powder"],
    "Vitasure": ["Polysaccharide powder", "Starch-based"],
    "Thrombin": ["JMI", "Bovine", "Human thrombin"],
    "Evithrom": ["Human thrombin", "Ethicon thrombin"],
    "RecothRom": ["rThrombin", "ZymoGenetics"],
    "Floseal": ["Gelatin-thrombin", "Baxter"],
    "SurgiFlo": ["Flowable gelatin", "Ethicon matrix"],
    "Tisseel": ["Fibrin sealant", "Fibrin glue", "Baxter fibrin"],
    "Evicel": ["Human fibrin", "Crosseal"],
    "Vitagel": ["Platelet-based", "Orthovita"],
    "Tachosil": ["Fibrin patch"],
    "Evarrest": ["Ethicon patch"],
    "Vistaseal": ["Dual Applicator"],
    "Woundclot": ["ABC", "Core Scientific"],
    "Perclot": ["AMP", "CryoLife"],
    "Endoclot": ["AMP Plus"],
    "Cryoseal": ["Fibrin system", "FS", "Thermogenesis"],
}

HEMOSTATIC_DEVICES_FLAT = flatten_dict_to_list(HEMOSTATIC_DEVICES)


HEMOSTATIC_DEVICES_MINI = {
    k: v
    for k, v in list(HEMOSTATIC_DEVICES.items())[:10]
}

HEMOSTATIC_DEVICES_MINI_FLAT = flatten_dict_to_list(HEMOSTATIC_DEVICES_MINI)



UROLOGY_INDICATORS = {
    "Urology Indicators": [
        # Original urological procedures
        "urological surgery",
        "vascular surgery",
        "renal transplant",
        "kidney transplant",
        "prostatectomy",
        "nephrectomy",
        "nephrolithotomy",
        "pyeloplasty",
        "ureterectomy",
        "cystectomy",
        "urethrectomy",
        "vasectomy",
        "hydrocelectomy",
        "varicocelectomy",
        "orchiectomy",
        "penectomy",
        "ovariectomy",
        "salpingectomy",
        "hysterectomy",
        "ovariohysterectomy",
        "salpingo-oophorectomy",
        "myomectomy",
        "trachelectomy",
        "vaginectomy",
        "vulvectomy",
        "angioplasty",
        "stenting",
        "endarterectomy",
        "thrombectomy",
        "aneurysm repair",
        "bypass",
        "aortocaval fistula repair",
        "aortoenteric fistula repair",
        "arteriovenous fistula surgery",
        "arteriovenous malformation surgery",
        "renal artery angioplasty",
        "endovascular reconstruction",
        "arterial reconstruction",
        "vein reconstruction",
        "inferior vena cava filter placement",
        "open vascular reconstruction",
        "vena cava reconstruction",
        # Synonyms - grouped by category
        # General urologic procedure synonyms
        "urology procedure",
        "urologic operation",
        "genitourinary surgery",
        "GU surgery",
        # Vascular procedure synonyms
        "vascular procedure",
        "blood vessel surgery",
        "angiosurgery",
        # Kidney/renal procedure synonyms
        "kidney transplantation",
        "renal grafting",
        "kidney grafting",
        "kidney removal",
        "renal excision",
        "percutaneous nephrolithotomy",
        "kidney stone removal",
        "renal stone removal",
        "ureteropelvic junction repair",
        "UPJ repair",
        "renal PTA",
        "kidney artery stenting",
        # Prostate procedure synonyms
        "radical prostatectomy",
        "prostate removal",
        "prostate excision",
        # Ureter/bladder procedure synonyms
        "ureter removal",
        "ureteral excision",
        "bladder removal",
        "bladder excision",
        "radical cystectomy",
        "urethra removal",
        "urethral excision",
        # Male reproductive procedure synonyms
        "sterilization procedure",
        "male sterilization",
        "hydrocele repair",
        "varicocele repair",
        "testicular vein ligation",
        "testicle removal",
        "testicular excision",
        "orchidectomy",
        "penis removal",
        "penile amputation",
        # Female reproductive procedure synonyms
        "ovary removal",
        "oophorectomy",
        "fallopian tube removal",
        "uterus removal",
        "uterine excision",
        "womb removal",
        "ovary and uterus removal",
        "ovary and fallopian tube removal",
        "oophorosalpingectomy",
        "fibroid removal",
        "uterine fibroid excision",
        "leiomyoma excision",
        "cervix removal",
        "cervical excision",
        "vagina removal",
        "vaginal excision",
        "colpectomy",
        "vulva removal",
        "vulvar excision",
        # Vascular/angioplasty procedure synonyms
        "balloon angioplasty",
        "percutaneous transluminal angioplasty",
        "stent placement",
        "stent insertion",
        "endovascular stenting",
        "carotid endarterectomy",
        "arterial plaque removal",
        "embolectomy",
        "AAA repair",
        "aortic aneurysm repair",
        "vascular bypass",
        "arterial bypass",
        "coronary bypass",
        "CABG",
        "aortocaval shunt repair",
        "aortoenteric connection repair",
        "AV fistula creation",
        "AV fistula repair",
        "vascular access surgery",
        "AVM surgery",
        "AVM resection",
        "EVAR",
        "endovascular aneurysm repair",
        "vascular graft",
        "arterial graft",
        "venous graft",
        "vascular graft placement",
        "IVC filter deployment",
        "caval filter insertion",
        "vascular bypass grafting",
        "IVC reconstruction",
        "caval reconstruction",
        
    ]
}

UROLOGY_INDICATORS_FLAT = flatten_dict_to_list(UROLOGY_INDICATORS)

UROLOGY_INDICATORS_MINI = {
    k: v[:10]
    for k, v in UROLOGY_INDICATORS.items()
}
UROLOGY_INDICATORS_MINI_FLAT = flatten_dict_to_list(UROLOGY_INDICATORS_MINI)



