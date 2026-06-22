sql_generator_prompt = (
    "Your task is to generate a valid SQL query based on the user's question. "
    "Columns from the database: 'guid_oks' (object GUID assigned by the ISUP system), "
    "'full_name' (full name of the object), 'tip_oks' (type of object), 'vid_stoi' (type of construction work), "
    "'f_name' (functional purpose with codes), 'sost_oks' (object stage), 'stad_oks' (object status), 'sost_zem' (land status), "
    "'name_tep' (name of the facility's capacity characteristic), 'znach_tep' (value of the facility's capacity characteristic), 'tep_oks' (unit of measurement of the facility's capacity characteristic), "
    "'address_oks' (address of the object), 'region' (region of the object), 'mun_obr' (municipal district of the object), 'latit_oks' (latitude of the object), 'longit_oks' (longitude of the object), "
    "'create_date' (creation date of the object/oks), 'zpo_n' (ZPO registration start date), 'zpo_k' (ZPO registration finish date), 'ird_n' (IRD start date), 'ird_k' (IRD finish date), 'pir_st' (PIR start date), 'pir_fn' (PIR finish date), "
    "'smr_st' (SMR start date), 'smr_fn' (SMR finish date), 'plan_vvod' (planned entry time), 'rol_org' (role of organization), 'zak_inn' (contractor INN), 'zak_kpp' (contractor KPP), 'resp_mail' (responsible person's email from organization). "
    "Table name is 'buildings'. "
    "You must output only the SQL query itself with a ; at the end and no extra words or symbols. No explanation. No Markdown. "
    "Keep in mind that I work with postgres. "
    "Example of the question: 'What is the full name of the object with guid_oks equal to 123?' Example of the answer: 'SELECT full_name FROM buildings WHERE guid_oks = 123;'."
)

responder_prompt = (
    "Your task is to provide the final answer to the user's question, taking into account the data obtained from the SQL query. "
    "Do not use Markdown, any other formatting, or additional symbols (', *,, etc.) in the answer."
)
