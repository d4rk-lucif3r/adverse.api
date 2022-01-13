import ast
import pickle
import os

import numpy as np
import pandas as pd
from faker import Faker
import pymongo
from pymongo import MongoClient


def postprocessing():

    f1 = Faker()

    df = pd.read_csv(
        os.path.abspath(os.path.join(os.getcwd(), "result_database/database.csv")),
        dtype="unicode",
    )

    df = df.drop_duplicates(subset="Web link of news", keep="last")

    df.reset_index(drop=True, inplace=True)

    df["Source Name"] = ""

    df["Source of Info"] = "News Paper"

    x = [f1.uuid4() for i in range(len(df))]

    df["uuid"] = x

    df["City/ State mentioned under the news"] = ""

    df.columns = [
        "Person Name mentioned in the news",
        "Organization Name mentioned in the news",
        "City/ State mentioned under the news",
        "Article Date",
        "Key word Used for identify the article",
        "HDFC Bank Name under News / Article",
        "Web link of news",
        "Source Name",
        "Source of Info",
        "uuid",
    ]

    # strip ending comma, spaces
    df["Person Name mentioned in the news"] = df[
        "Person Name mentioned in the news"
    ].apply(lambda x: x.strip(", "))
    df["Organization Name mentioned in the news"] = df[
        "Organization Name mentioned in the news"
    ].apply(lambda x: x.strip(", "))
    df["City/ State mentioned under the news"] = df[
        "City/ State mentioned under the news"
    ].apply(lambda x: x.strip(", "))
    df["Key word Used for identify the article"] = df[
        "Key word Used for identify the article"
    ].apply(lambda x: x.strip(", "))
    df["HDFC Bank Name under News / Article"] = df[
        "HDFC Bank Name under News / Article"
    ].apply(lambda x: x.strip(", "))
    df["Article Date"] = df["Article Date"].apply(lambda x: x.strip(", "))
    df["City of News Paper"] = ""  # document.pop('City of News Paper')

    dicts = df.to_dict(orient="records")
    client = MongoClient("localhost", 27017)
    db = client["adverse_db"]
    collection_batches = db["adverse_db"]
    cursor = collection_batches.find({}, {"_id": False})
    dbs = [database["Web link of news"] for database in cursor]

    for _dict in dicts:
        if _dict["Web link of news"] in dbs:
            continue
        else:
            collection_batches.insert_one(_dict)

    print("Post processing completed")

    return "Post processing Complete"


if __name__ == "__main__":

    postprocessing()
#     q_codes = []
#     q_codes_dict = {}


# df['father'] = df['father'].apply(qcode2val)

# df.to_csv('/home/ubuntu/data_temp/wiki_data1.csv')

#     q_codes = return_qcodes(df, 'first_name', q_codes)
#     print('first_name done')
#     q_codes = return_qcodes(df, 'last_name', q_codes)
#     q_codes = return_qcodes(df, 'gender', q_codes)
#     q_codes = return_qcodes(df, 'father', q_codes)
#     q_codes = return_qcodes(df, 'mother', q_codes)
#     print('starting qcodes2')
#     q_codes = return_qcodes2(df, 'citizen_country', q_codes)
#     q_codes = return_qcodes2(df, 'education', q_codes)
#     q_codes = return_qcodes2(df, 'occupation', q_codes)
#     q_codes = return_qcodes2(df, 'positions_held', q_codes)
#     q_codes = return_qcodes2(df, 'residence', q_codes)
#     q_codes = return_qcodes2(df, 'sources', q_codes)
#     q_codes = return_qcodes2(df, 'siblings', q_codes)
#     q_codes = return_qcodes2(df, 'spouse', q_codes)
#     q_codes = return_qcodes2(df, 'relatives', q_codes)
#     q_codes = return_qcodes2(df, 'political_associations', q_codes)
#     print('saved all the qcodes into list')

#     q_codes = set(q_codes)
#     q_codes = list(q_codes)

#     with open('data_temp/qcodes_list.pkl', 'wb') as f:
#         pickle.dump(q_codes, f)

#     print('saved all the qcodes into pickle')

#     for q_code in q_codes:
#         try:
#             q_codes_dict[q_code] = WikidataItem(get_entity_dict_from_api(q_code)).get_label()
#         except:
#             q_codes_dict[q_code] = np.nan

#     print('saved all the qcodes into dictionary')


#     with open('data_temp/qcodes_dict.pickle', 'wb') as handle:
#         pickle.dump(q_codes_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
