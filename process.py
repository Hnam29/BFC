import streamlit as st
import pandas as pd 
import random
from datetime import date
import datetime
from UI import * 
import plotly.express as px 
from streamlit_option_menu import option_menu 
from PIL import Image
import os
import pyexcel as p
import re
import io

bfc = Image.open('bfc.png')
st.set_page_config(page_title='Dashboard', page_icon=bfc, layout='wide', initial_sidebar_state='auto')
UI()
st.divider()
todayDate = datetime.date.today()
randomNum=(random.randint(0,10000))
# IMAGE
st.sidebar.image(bfc,caption='Nam:0983658980')
# HIDE STREAMLIT
hide_style ='''
            <style>
               #MainMenu {visibility:hidden}
               footer {visibility:hidden}
               header {visibility:hidden}
            </style>
            '''
st.markdown(hide_style,unsafe_allow_html=True)

@st.cache_resource
# process file
def process_file(file):
    file_type = None
    try:
        # Convert file to dataframe
        if file.name.endswith('.xlsx'):
            # df = pd.read_excel(file,sheet_name='sheet1',header=1)
            df = pd.read_excel(file,sheet_name='Sheet1',header=1)
            df.drop(['Unnamed: 5', 'Unnamed: 6', 'Unnamed: 8', '出口国家代码'], axis=1, inplace=True) # FOR IMPORT ONLY
            file_type = 'xlsx'
        elif file.name.endswith('.csv'):
            df = pd.read_csv(file,sheet_name='Sheet1',header=1)
            file_type = 'csv'
        else:
            st.error("Invalid file type. Expected CSV or XLSX file.")
            return 'Please upload the file', 'Please upload the file'
        return df, file_type
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None, None

def convert_df(df):
    # Create a writable file-like object in memory
    excel_buffer = io.BytesIO()
    # Save the DataFrame to the file-like object
    df.to_excel(excel_buffer, index=False)
    # Reset the buffer's position to the start for reading
    excel_buffer.seek(0)
    # Return the bytes of the Excel file
    return excel_buffer.getvalue()

# convert files
def convert_xls_to_xlsx(file_path):
    # Get the filename and extension
    filename, ext = os.path.splitext(file_path)
    # Create the new file name with .xlsx extension
    new_file_path = f"{filename}.xlsx"
    # Convert the .xls file to .xlsx using pyexcel
    p.save_book_as(file_name=file_path, dest_file_name=new_file_path)

# top analytics
def Analytics():
   total_record = (df['Tên_sản_phẩm'].count())
   all_price_ = float(df['Đơn_giá'].sum())
   all_total = float(df['Thành_tiền'].sum())

   total1,total2,total3= st.columns(3,gap='small')
   with total1:
      st.info('Total Record', icon="🔍")
      st.metric(label = 'BFC', value= f"{total_record}")
      y_col = st.selectbox('Select y column', options=df.columns[3:], key='y_col1')
      st.info(f'{y_col} by each month', icon="🔍")
      fig1 = px.line(df, x=df['Month'], y=y_col)
      fig1.update_layout(width=300)
      st.plotly_chart(fig1)
   with total2:
      st.info('Selling Price', icon="🔍")
      st.metric(label='BFC', value=f"{all_price_:,.0f}")
      options = [col for col in df.columns if col != 'Unnamed: 0']
      value = st.selectbox('Select value column', options=options, key='value')
      name  = st.selectbox('Select name column', options=options, key='name')
      st.info(f'Relationship between {value} and {name}', icon="🔍")
      fig2 = px.pie(df, values=value, names=name)
      fig2.update_layout(width=300)
      st.plotly_chart(fig2)
   with total3:
      st.info('Expected Profit', icon="🔍")
      st.metric(label= 'BFC',value=f"{all_total:,.0f}")
      options = ['Cty_nhập', 'Cty_nhập(TA)', 'Mã_số_thuế', 'Nhà_cung_cấp', 'Xuất_xứ', 'HScode', 'Đơn_vị', 'Thành_tiền', 'Đơn_giá']
      y_col = st.selectbox('Select y column', options=options, key='y_col3')
      st.info(f'{y_col} by each month', icon="🔍")
      try:
         fig3 = px.scatter(df, x=df['Month'], y=y_col, size=df['Số_lượng'])
         fig3.update_layout(width=300)
         st.plotly_chart(fig3)
      except ValueError:
         y_col = st.selectbox('Select y column (updated)', options=options[1:], key='y_col3.2')
         fig3 = px.scatter(df, x=df['Month'], y=y_col, size=df['Số_lượng'])
         fig3.update_layout(width=300)
         st.plotly_chart(fig3)
         

def Convert():
    # List of .xls files in the current directory
    xls_files = [file for file in os.listdir('.') if file.endswith('.xls')]
    # Convert each .xls file to .xlsx
    for xls_file in xls_files:
        convert_xls_to_xlsx(xls_file)

# SIDE BAR
with st.sidebar:
    selected = option_menu(
        menu_title='Menu', #required (default:None)
        options=['Preprocess','Merge','Analyze'], #required
        icons=['house','gear','book'], #optional -> find on Bootstrap
        menu_icon='cast', #optional
        default_index=0 #optional
    )


if selected == 'Preprocess':
    Convert()
    # PROCESS FILE
    file_uploads = st.file_uploader('Upload your file', accept_multiple_files=True)
    dfs = {}  # Dictionary to store DataFrames
    if file_uploads is not None:
        for file_upload in file_uploads:
            df, file_type = process_file(file_upload)
            if df is not None:
                filename = file_upload.name
                dfs[filename] = df  # Store the DataFrame in the dictionary
        # Show the uploaded DataFrames
        for filename, df in dfs.items():
                st.write(f"DataFrame for {filename}:",df)
                st.write('Total rows and columns:',df.shape)
                df = df.iloc[:, 0:17]
                # df.columns = ['Time', 'Mã_tờ_khai', 'Cty_nhập', 'Cty_nhập(TA)', 'Địa_chỉ', 'Mã_số_thuế',
                #               'Nhà_cung_cấp', 'Địa_chỉ(ncc)', 'Xuất_xứ', 'HScode', 'Tên_sản_phẩm',
                #               'Số_lượng', 'Đơn_vị', 'Cân_nặng', 'Thành_tiền', 'Đơn_vị', 'Đơn_giá']
                df.rename(columns={'日期':'Time','申报号':'Mã_tờ_khai','进口商（越南语)':'Cty_nhập','进口商英文':'Cty_nhập(TA)',    # FOR IMPORT ONLY
                                '进口商地址越语':'Địa_chỉ','税务代码':'Mã_số_thuế','出口商':'Nhà_cung_cấp','出口商地址':'Địa_chỉ(ncc)',
                                '出口国':'Xuất_xứ','HS编码':'HScode','商品描述':'Sản_phẩm','数量':'Số_lượng','数量单位':'Đơn_vị',
                                '重量':'Cân_nặng','金额':'Thành_tiền','金额单位':'Tiền_tệ','单价':'Đơn_giá'},inplace=True)
                df = df[(df['Sản_phẩm'].str.contains('beverage|food additives|food supplement|supplement|food additive|Phụ gia thực phẩm|thực phẩm|sx thực phẩm|chế biến thực phẩm|confectionery materials', flags=re.IGNORECASE, regex=True)) 
                        & (~df['Sản_phẩm'].str.contains('không dùng trong thực phẩm|not used in food', flags=re.IGNORECASE, regex=True))]
                df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d')
                df['Day'] = df['Time'].dt.day
                df['Month'] = df['Time'].dt.month
                df['Year'] = df['Time'].dt.year
                # Get the column to be moved
                col1 = df.pop('Day')
                col2 = df.pop('Month')
                col3 = df.pop('Year')
                # Insert cols at the desired position (index 0)
                df.insert(1, 'Day', col1)
                df.insert(2, 'Month', col2)
                df.insert(3, 'Year', col3)
                df.drop(['Time'], axis=1, inplace=True)
                # Final DataFrame 
                st.write(df)
                st.write('Total rows and columns:',df.shape)
                xlsx = convert_df(df)
                fname = st.text_input('Save file name as: ',key=f'{filename}')
                if fname:  # Check if fname is not empty
                    xlsx = convert_df(df)
                    st.download_button(
                        label="Download data as XLSX format",
                        data=xlsx,
                        file_name=f'{fname}.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'  # Set MIME type to XLSX
                    )

dfs = []
# Function to process the uploaded file
def process_file(file):
    df = pd.read_excel(file)  # Assuming the file is in Excel format, you can adjust this based on the actual file type
    return df

if selected == 'Merge':
    # File Upload
    file_uploads = st.file_uploader('Upload your files', accept_multiple_files=True)
    # Step 1: Read each uploaded file and store the data as separate DataFrames
    if file_uploads is not None:
        for file_upload in file_uploads:
            df = process_file(file_upload)
            if df is not None:
                dfs.append(df)  # Append the DataFrame to the list
    # Step 2: Concatenate the DataFrames along the rows axis (axis=0)
    if dfs:
        combined_df = pd.concat(dfs, axis=0, ignore_index=True)
        # Step 3: Display or use the combined DataFrame as needed
        st.write("Combined DataFrame:", combined_df)
        name = st.text_input('Save file name as: ')
        if name:
            excel = convert_df(combined_df)
            st.download_button(
                            label="Download data combined as XLSX format",
                            data=excel,
                            file_name=f'{name}.xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'  # Set MIME type to XLSX
            )
    else:
        st.warning("Please upload some files first.")               





if selected == 'Analyze':
    # PROCESS FILE + ANALYZE
    file_upload = st.file_uploader('Upload your file')
    df = pd.DataFrame()
    if file_upload is not None:
        df, file_type = process_file(file_upload)
        Analytics()

    # FORM 
    st.sidebar.header("Add New Record")
    options_form=st.sidebar.form("Option Form")
    day=options_form.number_input("Day",disabled=False)
    month=options_form.number_input("Month",disabled=False)
    year=options_form.number_input("Year",disabled=False)
    code=options_form.number_input("Code",disabled=False)
    imported_company=options_form.text_input("Company",value='BFC',disabled=False)
    address=options_form.text_input("Company Address",disabled=False)
    tax=options_form.number_input("Tax Code", max_value=9,disabled=False)
    supplier=options_form.text_input("Company Supplier",disabled=False)
    sup_address=options_form.text_input("Supplier Address",disabled=False)
    origin =options_form.selectbox("Origin",
      {"US","Germany",'Japan','China','Slovenia','Thailand','China','Spain','Singapore','India'})
    hscode =options_form.number_input("Tax Code", max_value=8,disabled=False)
    product =options_form.text_input("Product Name",value='',disabled=False)
    quantity = options_form.number_input("Quantity",min_value=1,disabled=False)
    unit = options_form.selectbox("Unit",{"KG","Ton",'Bag'})
    weight = options_form.number_input("Weight",disabled=False)
    price = options_form.number_input("Price per unit",min_value=0.1,step=0.1,disabled=False)
    total = options_form.number_input("Total",min_value=0.1,step=0.1,disabled=False)
    currency=options_form.text_input("Currency",value='USD',disabled=True)
    add_data = options_form.form_submit_button(label="Add")

   #when button is clicked
    if add_data:
        if imported_company != "" and product != "" and total != "":
            df = pd.concat([df, pd.DataFrame.from_records([{ 
            'Day': day,
            'Month':month,
            'Year':year,
            'Mã_tờ_khai':code,
            'Cty_nhập':imported_company,
            'Cty_nhập(TA)':imported_company,
            'Địa_chỉ': address,
            'Mã_số_thuế': tax,
            'Nhà_cung_cấp': supplier,
            'Địa_chỉ(ncc)': sup_address,
            'Xuất_xứ': origin,
            'HScode': hscode,
            'Tên_sản_phẩm': product,
            'Số_lượng': int(quantity),
            'Đơn_vị': unit,
            'Cân_nặng': float(weight),
            'Thành_tiền': float(quantity*price),
            'Đơn_vị': currency,
            'Đơn_giá': float(price)
            }])])
            try:
                df.to_excel("Titanium_Dioxide.xlsx",index=False)
            except:
                st.warning("Unable to write, Please close your dataset !!")
        else:
            st.sidebar.error("Fields required")

    with st.expander("Records"):
        selected = st.multiselect('Filter :', df.columns[1:])
        st.dataframe(df[selected],use_container_width=True)

    with st.expander("Cross Tab"):
        tab = pd.crosstab([df['Tên_sản_phẩm']],df['Số_lượng'], margins=True)
        st.dataframe(tab) 
        tab2 = pd.crosstab([df['Tên_sản_phẩm']],df['Xuất_xứ'], margins=True)
        st.dataframe(tab2) 

