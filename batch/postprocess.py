import pandas as pd
import math
import uuid
def postprocess():
    clean= ['Home','MPTrack','Shri','Smt','Dr','Mr','Mrs','Ms','cabinet','Minister','prime','Deputy','Ministry','Contact','Facebook','account','photo','mp','MP','Of','Biography','Email','Address','Roles','To','Read','more','Blog','Vacancies','Advertisement','Advertise','Office','Holding','Second','Member','Committee','Estimates','Fax','Find','Close','Links','Key','Figures','Stats','Statistics','Household','Full','name','Parks','Open','Menu','Languages','Opinion','Education','Address','Latest','Activity','Folketinget','Christiansborg','NA','PO','Father','Husband']
    banned = ['january','february','march','april','may','june','july','september','october','november','december','monday','tuesday','wednesday','thursday','friday','saturday','sunday','Party']
    try:
        df = pd.read_csv("result_database/database.csv",names=['Person Name mentioned in the news','Organization Name mentioned in the news','City/ State mentioned under the news','Created_date_time','Key word Used for identify the article', 'HDFC Bank Name under News / Article', 'Web link of news'],encoding= 'unicode_escape')
    except Exception as e:
        print(e)
        return
    df = df.applymap(str)
    # df.replace(to_replace = 'nan', value = '', inplace = True)
    #print("Before cleaning: length =",len(df))
    print("Postprocessing...")
    
    # df.dropna(subset=['Person Name mentioned in the news'],inplace=True)
    # df.drop_duplicates(subset=['Person Name mentioned in the news'], keep='first',inplace=True)
    # df.reset_index(drop=True, inplace=True)

    # for count,_ in enumerate(df['Person Name mentioned in the news']):
        # if  len(df['Person Name mentioned in the news'][count])<4:
            # df.drop(count,axis=0,inplace=True)
            # continue
        
        # for item in df['Person Name mentioned in the news'][count].split(' '):
            # if len(item)<2:
                # df.at[count, 'Person Name mentioned in the news'] = df['Person Name mentioned in the news'][count].replace(item,'')
            # for word in clean:
                # if word in item:
                    # new_val = df['Person Name mentioned in the news'][count].replace(word,'').strip()
                    # df.at[count, 'Person Name mentioned in the news'] = new_val
            # for ban in banned:
                # if ban in item.lower():
                    # df.drop(count,axis=0,inplace=True)
                    # break
            # else:
                # continue
            # break
                    

    # df.dropna(subset=['Person Name mentioned in the news'],inplace=True)
    # df.drop_duplicates(subset=['Person Name mentioned in the news'], keep='first',inplace=True)
    # df.reset_index(drop=True, inplace=True)
    # uuids = []
    # for _ in range(len(df)):
        # uuids.append(uuid.uuid4().hex)
    # df.insert(0, '_id', uuids)

    print("Postprocessing complete. Database contains {} rows".format(len(df)))
    #print("After cleaning: length =",len(df))
    df.to_csv("result_database/database.csv",index=False)
    #df.transpose().to_json('./result_database/database.json',orient='table',index=False)  # to save as json
