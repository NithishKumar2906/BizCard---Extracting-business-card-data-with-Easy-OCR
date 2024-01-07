#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().run_cell_magic('writefile', 'BizCard.py', 'import sqlite3\nimport pandas as pd\nimport streamlit as st\nfrom streamlit_option_menu import option_menu\nimport easyocr\nfrom PIL import Image\nimport cv2\nimport os\nimport matplotlib.pyplot as plt\nimport re\n\n\n# SETTING PAGE CONFIGURATIONS\nst.set_page_config(page_title="BizCardX: Extracting Business Card Data with OCR",\n                   layout="wide",\n                   initial_sidebar_state="expanded",\n                   menu_items={\'About\': """# This OCR app is created by *Sudhakar Bandari*!"""})\nst.markdown("BizCardX: Extracting Business Card Data with OCR", unsafe_allow_html=True)\n\n#=========hide the streamlit main and footer\nhide_default_format = """\n\n       """\nst.markdown(hide_default_format, unsafe_allow_html=True)\n\ndef app_background():\n    st.markdown(f""" """, unsafe_allow_html=True)\n\napp_background()\n\n# CREATING OPTION MENU\nselected = option_menu(None, ["Home","Upload & Extract","Modify"],\n                       icons=["home","cloud-upload-alt","edit"],\n                       default_index=0,\n                       orientation="horizontal",\n                       styles={"nav-link": {"font-size": "25px", "text-align": "centre", "margin": "0px", "--hover-color": "#AB63FA", "transition": "color 0.3s ease, background-color 0.3s ease"},\n                               "icon": {"font-size": "25px"},\n                               "container" : {"max-width": "6000px", "padding": "10px", "border-radius": "5px"},\n                               "nav-link-selected": {"background-color": "#63faab", "color": "white"}})\n\n# INITIALIZING THE EasyOCR READER\nreader = easyocr.Reader([\'en\'])\n\n# Connection to Sqlite3\nconn = sqlite3.connect("BizCard_extraction .db")\ncursor = conn.cursor()\n\ncursor.execute(\'\'\'CREATE TABLE IF NOT EXISTS card_data\n                   (id INTEGER PRIMARY KEY,\n                    company_name TEXT,\n                    card_holder TEXT,\n                    designation TEXT,\n                    mobile_number TEXT,\n                    email TEXT,\n                    website TEXT,\n                    area TEXT,\n                    city TEXT,\n                    state TEXT,\n                    pin_code TEXT,\n                    image BLOB\n                    )\'\'\')\n\n# HOME MENU\nif selected == "Home":\n        st.markdown("## :blue[**Technologies Used :**] Python, EasyOCR, Streamlit, SQL, Pandas")\n        st.markdown("## :blue[**Overview :**] The main purpose of this Streamlit App lets you upload Business Card images, extract info with easyOCR, and manage data (view, modify, delete). Save entries, including images, in a versatile database.")\n\n\n# UPLOAD AND EXTRACT MENU\nif selected == "Upload & Extract":\n    st.markdown("### Upload a Business Card")\n    uploaded_card = st.file_uploader("upload here", label_visibility="collapsed", type=["png", "jpeg", "jpg"])\n\n    if uploaded_card is not None:\n        # Create the \'uploaded_cards\' directory if it does not exist\n        if not os.path.exists("uploaded_cards"):\n           os.makedirs("uploaded_cards")\n\n        def save_card(uploaded_card):\n            with open(os.path.join("uploaded_cards", uploaded_card.name), "wb") as f:\n                f.write(uploaded_card.getbuffer())\n\n\n        save_card(uploaded_card)\n\n\n        def image_preview(image, res):\n            for (bbox, text, prob) in res:\n                # unpack the bounding box\n                (tl, tr, br, bl) = bbox\n                tl = (int(tl[0]), int(tl[1]))\n                tr = (int(tr[0]), int(tr[1]))\n                br = (int(br[0]), int(br[1]))\n                bl = (int(bl[0]), int(bl[1]))\n                cv2.rectangle(image, tl, br, (0, 255, 0), 2)\n                cv2.putText(image, text, (tl[0], tl[1] - 10),\n                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)\n            plt.rcParams[\'figure.figsize\'] = (15, 15)\n            plt.axis(\'off\')\n            plt.imshow(image)\n\n\n        # DISPLAYING THE UPLOADED CARD\n        col1, col2 = st.columns(2, gap="large")\n        with col1:\n            st.markdown("#     ")\n            st.markdown("#     ")\n            st.markdown("### You have uploaded the card")\n            st.image(uploaded_card)\n        # DISPLAYING THE CARD WITH HIGHLIGHTS\n        with col2:\n            st.markdown("#     ")\n            st.markdown("#     ")\n            with st.spinner("Processing image Please wait ..."):\n                st.set_option(\'deprecation.showPyplotGlobalUse\', False)\n                saved_img = os.getcwd() + "//" + "uploaded_cards" + "//" + uploaded_card.name\n                image = cv2.imread(saved_img)\n                res = reader.readtext(saved_img)\n                st.markdown("### Image Processed and Data Extracted")\n                st.pyplot(image_preview(image, res))\n        #easy OCR\n        saved_img = os.getcwd()+ "//" + "uploaded_cards"+ "//"+ uploaded_card.name\n        result = reader.readtext(saved_img,detail = 0,paragraph=False)\n        # /content/uploaded_cards/2.png\n        def binary_img(file_path):\n            with open(file_path, \'rb\') as file:\n                binaryData = file.read()\n            return binaryData\n\n\n        data = {"company_name": [],\n                "card_holder": [],\n                "designation": [],\n                "mobile_number": [],\n                "email": [],\n                "website": [],\n                "area": [],\n                "city": [],\n                "state": [],\n                "pin_code": [],\n                "image": binary_img(saved_img)\n                }\n\n        def get_data(res):\n            for ind, i in enumerate(res):\n                if "www " in i.lower() or "www." in i.lower():  # Website with \'www\'\n                    data["website"].append(i)\n                elif "WWW" in i:  # In case the website is in the next elements of the \'res\' list\n                    website = res[ind + 1] + "." + res[ind + 2]\n                    data["website"].append(website)\n                elif \'@\' in i:\n                    data["email"].append(i)\n                # To get MOBILE NUMBER\n                elif "-" in i:\n                    data["mobile_number"].append(i)\n                    if len(data["mobile_number"]) == 2:\n                        data["mobile_number"] = " & ".join(data["mobile_number"])\n                # To get COMPANY NAME\n                elif ind == len(res) - 1:\n                    data["company_name"].append(i)\n                # To get Card Holder Name\n                elif ind == 0:\n                    data["card_holder"].append(i)\n                #To get designation\n                elif ind == 1:\n                    data["designation"].append(i)\n\n                #To get area\n                if re.findall(\'^[0-9].+, [a-zA-Z]\',i):\n                    data["area"].append(i.split(\',\')[0])\n                elif re.findall(\'[0-9] [a-zA-z]+\',i):\n                    data["area"].append(i)\n                #To get city name\n                match1 = re.findall(\'.+St , ([a-zA-Z]+).+\',i)\n                match2 = re.findall(\'.+St,,([a-zA-Z]+).+\',i)\n                match3 = re.findall(\'^[E].*\',i)\n                if match1:\n                    data["city"].append(match1[0])\n                elif match2:\n                    data["city"].append(match2[0])\n                elif match3:\n                    data["city"].append(match3[0])\n\n                #To get state name\n                state_match = re.findall(\'[a-zA-Z]{9} +[0-9]\', i)\n                if state_match:\n                    data["state"].append(i[:9])\n                elif re.findall(\'^[0-9].+, ([a-zA-Z]+);\', i):\n                    data["state"].append(i.split()[-1])\n                if len(data["state"]) == 2:\n                    data["state"].pop(0)\n\n                #To get Pincode\n                if len(i) >= 6 and i.isdigit():\n                    data["pin_code"].append(i)\n                elif re.findall(\'[a-zA-Z]{9} +[0-9]\', i):\n                    data["pin_code"].append(i[10:])\n        get_data(result)\n\n        #Creating a dataframe and storing in DB\n        def create_df(data):\n            df = pd.DataFrame(data)\n            return df\n        df = create_df(data)\n        st.success("### Data Extracted ")\n        st.write(df)\n\n        if st.button("Upload to Database"):\n            for i,row in df.iterrows():\n                # here %S means string values\n                sql = """INSERT INTO card_data(company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,image)\n                                         VALUES (?,?,?,?,?,?,?,?,?,?,?)"""\n                cursor.execute(sql, tuple(row))\n                conn.commit()\n            st.success("#### Uploaded to database successfully!")\n\n# MODIFY MENU\nif selected == "Modify":\n    col1,col2,col3 = st.columns([3,3,2])\n    col2.markdown("## Alter or Delete the data here")\n    column1,column2 = st.columns(2,gap="large")\n    try :\n        with column1:\n            cursor.execute("Select card_holder FROM card_data")\n            result = cursor.fetchall()\n            business_cards = {}\n            for row in result:\n                business_cards[row[0]] = row[0]\n        selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))\n        st.markdown("#### Update or modify any data below")\n        cursor.execute(\n            "select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data WHERE card_holder=?",\n            (selected_card,))\n        result = cursor.fetchone()\n        # DISPLAYING ALL THE INFORMATIONS\n        company_name = st.text_input("Company_Name", result[0])\n        card_holder = st.text_input("Card_Holder", result[1])\n        designation = st.text_input("Designation", result[2])\n        mobile_number = st.text_input("Mobile_Number", result[3])\n        email = st.text_input("Email", result[4])\n        website = st.text_input("Website", result[5])\n        area = st.text_input("Area", result[6])\n        city = st.text_input("City", result[7])\n        state = st.text_input("State", result[8])\n        pin_code = st.text_input("Pin_Code", result[9])\n\n        if st.button("Commit changes to DB"):\n            # Update the information for the selected business card in the database\n            cursor.execute("""UPDATE card_data SET company_name=?,card_holder= ?,designation=?,mobile_number=?,email=?,website=?,area=?,city=?,state=?,pin_code=?\n                                        WHERE card_holder=?""", (\n            company_name, card_holder, designation, mobile_number, email, website, area, city, state, pin_code,\n            selected_card))\n            conn.commit()\n            st.success("Information updated in database successfully.")\n\n        with column2:\n            cursor.execute("SELECT card_holder FROM card_data")\n            result = cursor.fetchall()\n            business_cards = {}\n            for row in result:\n                business_cards[row[0]] = row[0]\n            selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))\n            st.write(f"### You have selected :green[**{selected_card}\'s**] card to delete")\n            st.write("#### Proceed to delete this card?")\n\n            if st.button("Yes Delete Business Card"):\n                cursor.execute(f"DELETE FROM card_data WHERE card_holder=\'{selected_card}\'")\n                conn.commit()\n                st.success("Business card information deleted from database.")\n    except:\n        st.warning("There is no data available in the database")\n\n    if st.button("View updated data"):\n        cursor.execute(\n            "select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data")\n        updated_df = pd.DataFrame(cursor.fetchall(),\n                                  columns=["Company_Name", "Card_Holder", "Designation", "Mobile_Number", "Email",\n                                           "Website", "Area", "City", "State", "Pin_Code"])\n        st.write(updated_df)\n')

