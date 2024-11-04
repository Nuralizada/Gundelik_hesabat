import streamlit as st
import pandas as pd
import datetime
import calendar

# Məlumatların yüklənməsi
fact_url = 'https://drive.google.com/uc?id=1lfRDeRq36e-wBn6undzT1DxlDiKst_8M&export=download'
fakt_df = pd.read_csv(fact_url)
plan_df = pd.read_excel("plan fakt.xlsx")
plan_f = pd.read_excel("Ekspeditor Fraxt.xlsx")
st.set_page_config(layout="wide")
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True)

# Tarix sütunlarını datetime formatına çevirmək
fakt_df['Tarix'] = pd.to_datetime(fakt_df['Tarix'], errors='coerce')
plan_df['Tarix'] = pd.to_datetime(plan_df['Tarix'], errors='coerce')
plan_f['Tarix'] = pd.to_datetime(plan_f['Tarix'], errors='coerce')

# Minimum başlanğıc tarixi (yanvarın 1-dən etibarən)
minimum_baslangic_tarix = datetime.date(datetime.datetime.now().year, 1, 1)

# Hər ayın neçə günə malik olduğunu hesablayan funksiya
def ayin_gunleri_ve_hecmi(year, month):
    days_in_month = calendar.monthrange(year, month)[1]
    return days_in_month

# Tam olmayan ay üçün plan həcmi hesablama funksiyası
def tam_olmayan_ay_hecmi(plan_df, year, month, start_day, end_day, rejim_secimi, ekspeditor=None, yuk=None, vaqon_novu=None):
    ayin_gunleri = ayin_gunleri_ve_hecmi(year, month)
    aylik_plan_hecmi = plan_df[
        (plan_df['Tarix'].dt.year == year) & 
        (plan_df['Tarix'].dt.month == month) & 
        (plan_df['Rejim'] == rejim_secimi)
    ]
    
    # Yük filtrini tətbiq etmək
    if yuk is not None:
        aylik_plan_hecmi = aylik_plan_hecmi[aylik_plan_hecmi['Əsas yük'] == yuk]

    # Ekspeditor filtrini tətbiq etmək
    if ekspeditor is not None:
        aylik_plan_hecmi = aylik_plan_hecmi[aylik_plan_hecmi['Ekspeditor'] == ekspeditor]

    # Vaqon növünə görə filtr tətbiq etmək
    if vaqon_novu is not None:
        aylik_plan_hecmi = aylik_plan_hecmi[aylik_plan_hecmi['Vaqon/konteyner'] == vaqon_novu]

    aylik_plan_hecmi = aylik_plan_hecmi['plan hecm'].sum()

    if aylik_plan_hecmi == 0:
        return 0

    gunluk_hecm = aylik_plan_hecmi / ayin_gunleri
    return gunluk_hecm * (end_day - start_day + 1)

# Plan həcmini seçilmiş tarix aralığında hesablamaq üçün funksiya
def plan_hecmi_tarix_araligina_gore(plan_df, baslangic_tarix, bitis_tarix, rejim_secimi, ekspeditor=None, yuk=None, vaqon_novu=None):
    total_plan_hecmi = 0
    
    # Əgər tarixlər eyni aydadırsa, yalnız həmin ayın günlərinə görə planı hesablamaq
    if baslangic_tarix.year == bitis_tarix.year and baslangic_tarix.month == bitis_tarix.month:
        total_plan_hecmi = tam_olmayan_ay_hecmi(plan_df, baslangic_tarix.year, baslangic_tarix.month, baslangic_tarix.day, bitis_tarix.day, rejim_secimi, ekspeditor, yuk, vaqon_novu)
    else:
        # Başlanğıc ayı üçün qismən plan həcmini hesablamaq
        total_plan_hecmi += tam_olmayan_ay_hecmi(plan_df, baslangic_tarix.year, baslangic_tarix.month, baslangic_tarix.day, ayin_gunleri_ve_hecmi(baslangic_tarix.year, baslangic_tarix.month), rejim_secimi, ekspeditor, yuk, vaqon_novu)

        # Bitmə ayı üçün qismən plan həcmini hesablamaq
        total_plan_hecmi += tam_olmayan_ay_hecmi(plan_df, bitis_tarix.year, bitis_tarix.month, 1, bitis_tarix.day, rejim_secimi, ekspeditor, yuk, vaqon_novu)

        # İki tarix arasında olan tam aylar üçün plan həcmini toplamaq
        if baslangic_tarix.year != bitis_tarix.year or baslangic_tarix.month != bitis_tarix.month:
            for year in range(baslangic_tarix.year, bitis_tarix.year + 1):
                month_start = 1 if year != baslangic_tarix.year else baslangic_tarix.month + 1
                month_end = 12 if year != bitis_tarix.year else bitis_tarix.month - 1

                for month in range(month_start, month_end + 1):
                    aylik_hecm = plan_df[
                        (plan_df['Tarix'].dt.year == year) & 
                        (plan_df['Tarix'].dt.month == month) & 
                        (plan_df['Rejim'] == rejim_secimi)
                    ]
                    
                    if ekspeditor is not None:
                        aylik_hecm = aylik_hecm[aylik_hecm['Ekspeditor'] == ekspeditor]
                    
                    if yuk is not None:
                        aylik_hecm = aylik_hecm[aylik_hecm['Əsas yük'] == yuk]

                    if vaqon_novu is not None:
                        aylik_hecm = aylik_hecm[aylik_hecm['Vaqon/konteyner'] == vaqon_novu]

                    aylik_hecm = aylik_hecm['plan hecm'].sum()
                    total_plan_hecmi += aylik_hecm

    return total_plan_hecmi



# Tam olmayan ay üçün plan həcmi hesablama funksiyası
def tam_olmayan_ay_hecmi_f(plan_f, year, month, start_day, end_day, rejim_secimi, ekspeditor=None):
    ayin_gunleri_f = ayin_gunleri_ve_hecmi(year, month)
    aylik_plan_hecmi_f = plan_f[
        (plan_f['Tarix'].dt.year == year) & 
        (plan_f['Tarix'].dt.month == month) & 
        (plan_f['Rejim'] == rejim_secimi)
    ]
    
    # Ekspeditor filtrini tətbiq etmək
    if ekspeditor is not None:
        aylik_plan_hecmi_f = aylik_plan_hecmi_f[aylik_plan_hecmi_f['Ekspeditor'] == ekspeditor]

    aylik_plan_hecmi_f = aylik_plan_hecmi_f['Həcm_fraxt'].sum()

    if aylik_plan_hecmi_f == 0:
        return 0

    gunluk_hecm_f = aylik_plan_hecmi_f / ayin_gunleri_f
    return gunluk_hecm_f * (end_day - start_day + 1)

# Plan həcmini seçilmiş tarix aralığında hesablamaq üçün funksiya
def plan_hecmi_tarix_araligina_gore_f(plan_f, baslangic_tarix, bitis_tarix, rejim_secimi, ekspeditor=None):
    total_plan_hecmi_f = 0
    
    # Əgər tarixlər eyni aydadırsa, yalnız həmin ayın günlərinə görə planı hesablamaq
    if baslangic_tarix.year == bitis_tarix.year and baslangic_tarix.month == bitis_tarix.month:
        total_plan_hecmi_f = tam_olmayan_ay_hecmi_f(plan_f, baslangic_tarix.year, baslangic_tarix.month, baslangic_tarix.day, bitis_tarix.day, rejim_secimi, ekspeditor)
    else:
        # Başlanğıc ayı üçün qismən plan həcmini hesablamaq
        total_plan_hecmi_f += tam_olmayan_ay_hecmi_f(plan_f, baslangic_tarix.year, baslangic_tarix.month, baslangic_tarix.day, ayin_gunleri_ve_hecmi(baslangic_tarix.year, baslangic_tarix.month), rejim_secimi, ekspeditor)

        # Bitmə ayı üçün qismən plan həcmini hesablamaq
        total_plan_hecmi_f += tam_olmayan_ay_hecmi_f(plan_f, bitis_tarix.year, bitis_tarix.month, 1, bitis_tarix.day, rejim_secimi, ekspeditor)

        # İki tarix arasında olan tam aylar üçün plan həcmini toplamaq
        if baslangic_tarix.year != bitis_tarix.year or baslangic_tarix.month != bitis_tarix.month:
            for year in range(baslangic_tarix.year, bitis_tarix.year + 1):
                month_start = 1 if year != baslangic_tarix.year else baslangic_tarix.month + 1
                month_end = 12 if year != bitis_tarix.year else bitis_tarix.month - 1

                for month in range(month_start, month_end + 1):
                    aylik_hecm_f = plan_f[
                        (plan_f['Tarix'].dt.year == year) & 
                        (plan_f['Tarix'].dt.month == month) & 
                        (plan_f['Rejim'] == rejim_secimi)
                    ]
                    
                    if ekspeditor is not None:
                        aylik_hecm_f = aylik_hecm_f[aylik_hecm_f['Ekspeditor'] == ekspeditor]

                    aylik_hecm_f = aylik_hecm_f['Həcm_fraxt'].sum()
                    total_plan_hecmi_f += aylik_hecm_f

    return total_plan_hecmi_f

# Cədvəl vizuallaşdırma funksiyası
def create_table(dataframe, title):
    st.markdown(f"<h4 style='text-align: left; color: #e02020;'>{title}</h4>", unsafe_allow_html=True)  # Başlıq qırmızı
    dataframe.fillna(0, inplace=True)  # NaN dəyərləri 0 ilə əvəz et
    st.table(dataframe.style.format({
        'Plan': "{:,.0f}",
        'Fakt': "{:,.0f}",
        'Yerinə yetirmə faizi': "{:.0f}%",
        'Plan(Fraxt)': "{:,.0f}",
        'Plan(KM)': "{:,.0f}",
        'Yerinə yetirmə faizi(Fraxt)': "{:.0f}%"
    }).set_table_styles([{
        'selector': 'thead th', 'props': [('background-color', '#2b2563'), ('color', 'white')]
    }, {
        'selector': 'tbody td', 'props': [('text-align', 'center'), ('background-color', '#f0f0f5')]
    }]))  # Cədvəlin fonu mavi

# Səhifəni seçin
page = st.sidebar.radio(
    "Səhifəni seçin",
    ("Report", "Current Month,Current Year", "Digər yüklər", "Tranzit")
)

# Card tərzi üçün tərz
def card(title, value):
    st.markdown(f"""
        <div style="background-color: #e7e6eb; padding: 10px; border-radius: 10px; margin-bottom: 10px; text-align: center;">
            <p style="font-size: 24px; font-weight: bold; color: #302a6b; margin: 0;">{value}</p>
            <h3 style="margin: 0; font-size: 14px; padding-top: 0px; color: #302a6b;">{title}</h3>
        </div>
    """, unsafe_allow_html=True)

if page == "Current Month,Current Year":
    st.markdown(f"""
        <h3 style='text-align: left; color: #2b2563;'>
            Rejimlər üzrə aylıq və illik daşınma statistikası: {calendar.month_name[datetime.datetime.now().month]} {datetime.datetime.now().year}
        </h3>
    """, unsafe_allow_html=True)

    # Girişlər üçün üç sütun istifadə edin
    col1, col2, col3 = st.columns(3)

    with col1:
        baslangic_tarix = st.date_input(
            "Başlanğıc tarixi", 
            value=None,
            min_value=minimum_baslangic_tarix,
            max_value=fakt_df['Tarix'].max().date()
        )

    with col2:
        bitis_tarix = st.date_input(
            "Bitiş tarixi", 
            value=None,  
            min_value=minimum_baslangic_tarix,
            max_value=datetime.date.today() - datetime.timedelta(days=1)
        )

    with col3:
        rejim_secimi = st.selectbox(
            "Rejim Seçin", 
            options=fakt_df['Rejim'].unique(),
            index=0
        )

    if not baslangic_tarix or not bitis_tarix:
        st.warning("Zəhmət olmasa tarix seçin.")
    else:
        if baslangic_tarix > bitis_tarix:
            st.error("Zəhmət olmasa düzgün tarix aralığı seçin: Başlanğıc tarixi bitiş tarixindən əvvəl olmalıdır.")
        else:
            ### Yüklər üzrə məlumatları toplamaq
            yukler = fakt_df['əsas_yüklər'].unique()
            total_plan_hecmi = []
            total_fakt_hecmi = []
            total_plan_hecmi_f = []
            for yuk in yukler:
                # Plan həcmini seçilmiş tarix aralığına görə hesablamaq
                plan_hecmi = plan_hecmi_tarix_araligina_gore(plan_df, baslangic_tarix, bitis_tarix, rejim_secimi, yuk=yuk)
                total_plan_hecmi.append(plan_hecmi)

                # Faktik həcmi hesablamaq
                fakt_hecmi = fakt_df[
                    (fakt_df['Tarix'].dt.date >= baslangic_tarix) & 
                    (fakt_df['Tarix'].dt.date <= bitis_tarix) & 
                    (fakt_df['Rejim'] == rejim_secimi) & 
                    (fakt_df['əsas_yüklər'] == yuk)
                ]['Həcm_fakt'].sum()
                total_fakt_hecmi.append(fakt_hecmi)

            netice_df = pd.DataFrame({
                'Yükün adı': yukler,
                'Plan': total_plan_hecmi,
                'Fakt': total_fakt_hecmi
            })

            netice_df['Yerinə yetirmə faizi'] = (netice_df['Fakt'] / netice_df['Plan']).replace([float('inf'), -float('inf')], 1).fillna(0) * 100
            netice_df['Yerinə yetirmə faizi'].fillna(0, inplace=True)
            netice_df = netice_df[(netice_df['Plan'] != 0) | (netice_df['Fakt'] != 0)]

            # "Digər yüklər" sətrini ayırın və cədvəlin ən aşağısına əlavə edin
            diger_yukler = netice_df[netice_df['Yükün adı'] == 'Digər yüklər']
            netice_df = netice_df[netice_df['Yükün adı'] != 'Digər yüklər']
            netice_df = netice_df.sort_values(by='Plan', ascending=False)  # Azalan sırada düzülür
            netice_df = pd.concat([netice_df, diger_yukler], ignore_index=True)

            # Cardları yan-yana göstərmək
            col1, col2, col3 = st.columns(3)

            total_plan_hecmi_sum = netice_df['Plan'].sum()
            total_fakt_hecmi_sum = netice_df['Fakt'].sum()
            yerinə_yetirme_faizi_sum = (total_fakt_hecmi_sum / total_plan_hecmi_sum) * 100 if total_plan_hecmi_sum > 0 else 0

            with col1:
                card("Plan", f"{total_plan_hecmi_sum:,.0f}")
            with col2:
                card("Fakt", f"{total_fakt_hecmi_sum:,.0f}")
            with col3:
                card("Yerinə yetirmə faizi", f"{yerinə_yetirme_faizi_sum:.0f}%")

            # Yüklər üzrə cədvəli yaradın
            create_table(netice_df, "Yüklər üzrə plan və fakt həcmləri")

            ### Ekspeditorlar üzrə məlumatları toplamaq
            ekspeditorlar = plan_df['Ekspeditor'].unique()
            total_plan_hecmi_eksp = []
            total_fakt_hecmi_eksp = []
            total_plan_hecmi_eksp_f = []
            
            for ekspeditor in ekspeditorlar:
                plan_hecmi_eksp = plan_hecmi_tarix_araligina_gore(plan_df, baslangic_tarix, bitis_tarix, rejim_secimi, ekspeditor=ekspeditor)
                total_plan_hecmi_eksp.append(plan_hecmi_eksp)
                
                plan_hecmi_eksp_f = plan_hecmi_tarix_araligina_gore_f(plan_f, baslangic_tarix, bitis_tarix, rejim_secimi, ekspeditor=ekspeditor)
                total_plan_hecmi_eksp_f.append(plan_hecmi_eksp_f)

                fakt_hecmi_eksp = fakt_df[
                    (fakt_df['Tarix'].dt.date >= baslangic_tarix) & 
                    (fakt_df['Tarix'].dt.date <= bitis_tarix) & 
                    (fakt_df['Rejim'] == rejim_secimi) & 
                    (fakt_df['Eksp'] == ekspeditor)
                ]['Həcm_fakt'].sum()

                total_fakt_hecmi_eksp.append(fakt_hecmi_eksp)

            combined_df = pd.DataFrame({
                'Ekspeditor': ekspeditorlar,
                'Plan(KM)': total_plan_hecmi_eksp,
                'Fakt': total_fakt_hecmi_eksp
            })

            # Yerinə Yetirmə Faizi sütununu əlavə edin
            combined_df['Yerinə yetirmə faizi'] = (combined_df['Fakt'] / combined_df['Plan(KM)']).replace([float('inf'), -float('inf')],1).fillna(0) * 100
            combined_df['Yerinə yetirmə faizi'].fillna(0, inplace=True)

            # Fraxt Həcmi üçün yeni sütunu əlavə edin
            combined_df['Plan(Fraxt)'] = total_plan_hecmi_eksp_f  # Həcm fraxt sütunu əlavə edin

            # Həcm fraxtın Yerinə Yetirmə Faizi sütununu əlavə edin
            combined_df['Yerinə yetirmə faizi(Fraxt)'] = (combined_df['Fakt'] / combined_df['Plan(Fraxt)']).replace([float('inf'), -float('inf')],1 ).fillna(0) * 100
            combined_df['Yerinə yetirmə faizi(Fraxt)'].fillna(0, inplace=True)

            # Plan və faktın boş olduğu ekspeditorları tapın
            fakt_ekspeditorlar = fakt_df['Eksp'].unique()
            plan_ekspeditorlar = plan_df['Ekspeditor'].unique()

            
            # Indeksi sıfırlayaraq sıra saylarını yığışdırırıq
            combined_df = combined_df.reset_index(drop=True)

            # Ekspeditorlar cədvəlini yaradın
            create_table(combined_df.sort_values(by='Plan(KM)', ascending=False), "Ekspeditorlar üzrə plan və fakt həcmləri")

            ### Vaqon növü üzrə məlumatları toplamaq
            vaqon_novleri = fakt_df['vaqon_növü'].unique()
            total_plan_hecmi_vaqon = []
            total_fakt_hecmi_vaqon = []

            for vaqon_novu in vaqon_novleri:
                plan_hecmi_vaqon = plan_hecmi_tarix_araligina_gore(plan_df, baslangic_tarix, bitis_tarix, rejim_secimi, vaqon_novu=vaqon_novu)
                total_plan_hecmi_vaqon.append(plan_hecmi_vaqon)

                fakt_hecmi_vaqon = fakt_df[
                    (fakt_df['Tarix'].dt.date >= baslangic_tarix) & 
                    (fakt_df['Tarix'].dt.date <= bitis_tarix) & 
                    (fakt_df['Rejim'] == rejim_secimi) & 
                    (fakt_df['vaqon_növü'] == vaqon_novu)
                ]['Həcm_fakt'].sum()

                total_fakt_hecmi_vaqon.append(fakt_hecmi_vaqon)

            vaqon_df = pd.DataFrame({
                'Vaqon tipi': vaqon_novleri,
                'Plan': total_plan_hecmi_vaqon,
                'Fakt': total_fakt_hecmi_vaqon
            })

            vaqon_df['Yerinə yetirmə faizi'] = (vaqon_df['Fakt'] / vaqon_df['Plan']).replace([float('inf'), -float('inf')], 1).fillna(0) * 100
            vaqon_df['Yerinə yetirmə faizi'].fillna(0, inplace=True)

            # Indeksi sıfırlayaraq sıra saylarını yığışdırırıq
            vaqon_df = vaqon_df.reset_index(drop=1)

            # Vaqon cədvəlini yaradın
            create_table(vaqon_df.sort_values(by='Plan', ascending=False), "Vaqon növü üzrə plan və fakt həcmləri")

elif page == "Tranzit":
    
        

elif page == "Digər yüklər":
    st.markdown(f"""
        <h3 style='text-align: left; color: #2b2563;'>
            Rejimlər üzrə digər yüklərin aylıq və illik göstəriciləri: {calendar.month_name[datetime.datetime.now().month]} {datetime.datetime.now().year}
        </h3>
    """, unsafe_allow_html=True)

    # Girişlər üçün üç sütun istifadə edin
    col1, col2, col3 = st.columns(3)

    with col1:
        baslangic_tarix = st.date_input(
            "Başlanğıc tarixi", 
            value=None,
            min_value=minimum_baslangic_tarix,
            max_value=fakt_df['Tarix'].max().date()
        )

    with col2:
        bitis_tarix = st.date_input(
            "Bitiş tarixi", 
            value=None,  
            min_value=minimum_baslangic_tarix,
            max_value=datetime.date.today() - datetime.timedelta(days=1)
        )

    with col3:
        rejim_secimi = st.selectbox(
            "Rejim Seçin", 
            options=fakt_df['Rejim'].unique(),
            index=0
        )

    if not baslangic_tarix or not bitis_tarix:
        st.warning("Zəhmət olmasa tarix seçin.")
    else:
        if baslangic_tarix > bitis_tarix:
            st.error("Zəhmət olmasa düzgün tarix aralığı seçin: Başlanğıc tarixi bitiş tarixindən əvvəl olmalıdır.")
        else:
            ### Yüklər üzrə məlumatları toplamaq
            yukler = fakt_df['əsas_yüklər'].unique()
            total_plan_hecmi = []
            total_fakt_hecmi = []

            for yuk in yukler:
                # Plan həcmini seçilmiş tarix aralığına və rejimə görə hesablamaq
                plan_hecmi = plan_hecmi_tarix_araligina_gore(plan_df, baslangic_tarix, bitis_tarix, rejim_secimi, yuk=yuk)
                total_plan_hecmi.append(plan_hecmi)

                # Faktik həcmi hesablamaq
                fakt_hecmi = fakt_df[
                    (fakt_df['Tarix'] >= pd.to_datetime(baslangic_tarix)) & 
                    (fakt_df['Tarix'] <= pd.to_datetime(bitis_tarix)) & 
                    (fakt_df['Rejim'] == rejim_secimi) & 
                    (fakt_df['əsas_yüklər'] == yuk)
                ]['Həcm_fakt'].sum()
                total_fakt_hecmi.append(fakt_hecmi)

            netice_df = pd.DataFrame({
                'Yükün adı': yukler,
                'Plan': total_plan_hecmi,
                'Fakt': total_fakt_hecmi
            })

            netice_df['Yerinə yetirmə faizi'] = (netice_df['Fakt'] / netice_df['Plan']).replace([float('inf'), -float('inf')], 1).fillna(0) * 100
            netice_df['Yerinə yetirmə faizi'].fillna(0, inplace=True)
            netice_df = netice_df[(netice_df['Plan'] != 0) | (netice_df['Fakt'] != 0)]

            # "Digər yüklər" sətrini ayırın və cədvəlin ən aşağısına əlavə edin
            diger_yukler = netice_df[netice_df['Yükün adı'] == 'Digər yüklər']
            netice_df = netice_df[netice_df['Yükün adı'] != 'Digər yüklər']
            netice_df = netice_df.sort_values(by='Plan', ascending=False)  # Azalan sırada düzülür
            netice_df = pd.concat([netice_df, diger_yukler], ignore_index=True)

            # Cardları yan-yana göstərmək
            col1, col2, col3 = st.columns(3)

            total_plan_hecmi_sum = netice_df['Plan'].sum()
            total_fakt_hecmi_sum = netice_df['Fakt'].sum()
            yerinə_yetirme_faizi_sum = (total_fakt_hecmi_sum / total_plan_hecmi_sum) * 100 if total_plan_hecmi_sum > 0 else 0

            with col1:
                card("Plan", f"{total_plan_hecmi_sum:,.0f}")
            with col2:
                card("Fakt", f"{total_fakt_hecmi_sum:,.0f}")
            with col3:
                card("Yerinə yetirmə faizi", f"{yerinə_yetirme_faizi_sum:.0f}%")

            # Yüklər üzrə cədvəli yaradın
            create_table(netice_df, "Yüklər üzrə plan və fakt həcmləri")

            ### İkinci cədvəl - "Digər yüklər" məlumatlarını göstərmək
            diger_yukler_df = fakt_df[
                (fakt_df['əsas_yüklər'] == 'Digər yüklər') & 
                (fakt_df['Tarix'] >= pd.to_datetime(baslangic_tarix)) & 
                (fakt_df['Tarix'] <= pd.to_datetime(bitis_tarix)) &
                (fakt_df['Rejim'] == rejim_secimi)  # Rejim filtrini əlavə et
            ]

            # Həcm faktı 0 olanları süzün
            diger_yukler_df = diger_yukler_df[diger_yukler_df['Həcm_fakt'] > 0]

            # Malın adı üzrə qruplaşdırma
            diger_yukler_grouped = diger_yukler_df.groupby('Malın_adı')['Həcm_fakt'].sum().reset_index()

            # Cədvəli azalan həcmlərə görə sıralamaq
            diger_yukler_grouped = diger_yukler_grouped.sort_values(by='Həcm_fakt', ascending=False)

            # Cədvəl yaradın, ədədləri ayrı şəkildə göstərmək üçün formatlayın
            diger_yukler_grouped['Həcm_fakt'] = diger_yukler_grouped['Həcm_fakt'].map('{:,.0f}'.format)  # Vergüllə ayırın

            # İndeksi sıfırlayaraq sıralı indeks yaradın
            diger_yukler_grouped.reset_index(drop=True, inplace=True)

            # Cədvəl yaradın
            create_table(diger_yukler_grouped, "Digər yüklər üzrə fakt həcmləri")


import streamlit as st
import pandas as pd
import datetime
import calendar
from PIL import Image

# Məlumatların yüklənməsi
fact_url = 'https://drive.google.com/uc?id=1lfRDeRq36e-wBn6undzT1DxlDiKst_8M&export=download'
fakt_df = pd.read_csv(fact_url)
fakt_df['Tarix'] = pd.to_datetime(fakt_df['Tarix'], errors='coerce')

plan_df = pd.read_excel("plan fakt.xlsx")
plan_df['Tarix'] = pd.to_datetime(plan_df['Tarix'], errors='coerce')

# Minimum başlanğıc tarixi (yanvarın 1-dən etibarən)
minimum_baslangic_tarix = datetime.date(datetime.datetime.now().year, 1, 1)

# Hər ayın neçə günə malik olduğunu hesablayan funksiya
def ayin_gunleri_ve_hecmi(year, month):
    days_in_month = calendar.monthrange(year, month)[1]
    return days_in_month

# Plan həcmini seçilmiş tarix aralığında hesablamaq üçün funksiya
def plan_hecmi_tarix_araligina_gore(plan_df, baslangic_tarix, bitis_tarix, rejim_secimi=None):
    total_plan_hecmi = 0
    
    # Rejim filtrini tətbiq edək
    if rejim_secimi is not None and rejim_secimi != "Bütün rejimlər":
        plan_df = plan_df[plan_df['Rejim'] == rejim_secimi]

    # Tam aylar üçün plan həcmini hesablayır
    for year in range(baslangic_tarix.year, bitis_tarix.year + 1):
        for month in range(1, 13):
            if (year == baslangic_tarix.year and month < baslangic_tarix.month) or (year == bitis_tarix.year and month > bitis_tarix.month):
                continue
            
            if year == bitis_tarix.year and month == bitis_tarix.month:
                # Bitmə ayı üçün qismən plan həcmini hesablamaq
                days_in_month = calendar.monthrange(year, month)[1]
                total_plan_hecmi += plan_df[(plan_df['Tarix'].dt.month == month) & (plan_df['Tarix'].dt.year == year)]['plan hecm'].sum() * (bitis_tarix.day / days_in_month)
            else:
                # Tam aylar üçün plan həcmini toplamaq
                total_plan_hecmi += plan_df[(plan_df['Tarix'].dt.month == month) & (plan_df['Tarix'].dt.year == year)]['plan hecm'].sum()

    return total_plan_hecmi

# Cədvəl vizuallaşdırma funksiyası
def create_table(dataframe, title):
    st.markdown(f"<h4 style='text-align: left; color: #e02020;'>{title}</h4>", unsafe_allow_html=True)  # Başlıq qırmızı
    dataframe.fillna(0, inplace=True)  # NaN dəyərləri 0 ilə əvəz et
    st.table(dataframe.style.format({
        'Plan': "{:,.0f}",
        'Fakt': "{:,.0f}",
        'Yerinə yetirmə faizi': "{:.0f}%",
        'Daşınma payı': "{:.0f}%",

    }).set_table_styles([{
        'selector': 'thead th', 'props': [('background-color', '#2b2563'), ('color', 'white')]
    }, {
        'selector': 'tbody td', 'props': [('text-align', 'center'), ('background-color', '#f0f0f5')]
    }]))  # Cədvəlin fonu mavi





if page == "Report":
    # Şəkili əlavə edin
    image = Image.open('Picture1.png')

    # İki sütun yaratmaq (birincisi kiçik şəkil üçün, ikincisi başlıq üçün)
    col1, col2 = st.columns([0.1, 0.9])
    
    # Şəkili solda kiçik sütunda göstər
    with col1:
        st.image(image, width=100)
    
    # Sağ tərəfdə mərkəzləşdirilmiş başlıq
    with col2:
        st.markdown("<center><h3 style='color: #16105c;'>Ekspeditorlar üzrə aylıq və illik daşınma məlumatları</h3></center>", unsafe_allow_html=True)

    # Tarix seçimi üçün üç sütun yaradın
    col_start_date, col_end_date, col_rejim = st.columns([1, 1, 1])  # Eyni sətrdə tarixi seçirik
    
    with col_start_date:
        # Başlanğıc tarixi seçimi
        start_date = st.date_input("Başlanğıc tarixi", value=datetime.date(datetime.datetime.now().year, 1, 1), min_value=minimum_baslangic_tarix, max_value=datetime.date.today() - datetime.timedelta(days=1))
    
    with col_end_date:
        # Bitiş tarixi seçimi
        end_date = st.date_input("Bitiş tarixi", value=datetime.date.today() - datetime.timedelta(days=1), min_value=minimum_baslangic_tarix, max_value=datetime.date.today() - datetime.timedelta(days=1))

    with col_rejim:
        # Rejim seçimi üçün multiselect əlavə edirik
        rejim_options = ["Bütün rejimlər"] + fakt_df['Rejim'].unique().tolist()
        selected_rejim = st.selectbox("Rejim:", rejim_options, index=0)

    # Tarix seçilmədiyi halda şərti yoxlayın
    if start_date and end_date:
        # Plan həcmini hesablamaq
        total_plan_hecmi = plan_hecmi_tarix_araligina_gore(plan_df, start_date, end_date)

        # Fakt həcmini hesablamaq
        total_fakt_hecmi = fakt_df[(fakt_df['Tarix'] >= pd.to_datetime(start_date)) & (fakt_df['Tarix'] <= pd.to_datetime(end_date))]['Həcm_fakt'].sum()

        # Yerinə yetirmə faizini hesabla
        yerinə_yetirmə_faizi_sum = (total_fakt_hecmi / total_plan_hecmi * 100) if total_plan_hecmi > 0 else 0

        # Cardları yan-yana göstərmək
        col1, col2, col3 = st.columns(3)

        # Card 1: Plan Həcmi
        with col1:
            st.markdown(f"""
                <div style="background-color:#e0e0e0; padding:10px; border-radius:8px; text-align:center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                    <h2 style='color: #30336b; margin: 0;'>{total_plan_hecmi:,.0f}</h2>
                    <p style='color: #30336b; margin: 0;'>Plan (ümumi)</p>
                </div>
            """, unsafe_allow_html=True)

        # Card 2: Fakt Həcmi
        with col2:
            st.markdown(f"""
                <div style="background-color:#e0e0e0; padding:10px; border-radius:8px; text-align:center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                    <h2 style='color: #30336b; margin: 0;'>{total_fakt_hecmi:,.0f}</h2>
                    <p style='color: #30336b; margin: 0;'>Fakt (ümumi)</p>
                </div>
            """, unsafe_allow_html=True)

        # Card 3: Yerinə Yetirmə Faizi
        with col3:
            st.markdown(f"""
                <div style="background-color:#e0e0e0; padding:10px; border-radius:8px; text-align:center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                    <h2 style='color: #30336b; margin: 0;'>{yerinə_yetirmə_faizi_sum:.0f}%</h2>
                    <p style='color: #30336b; margin: 0;'>Yerinə Yetirmə Faizi</p>
                </div>
            """, unsafe_allow_html=True)

        # Cədvəl yaradılması
        if start_date and end_date:
            # Cədvəl üçün məlumatlar
            data = []
            # Bütün rejimlər üçün plan və fakt həcmlərini hesablamaq
            rejim_list = plan_df['Rejim'].unique()  # Bütün rejimləri əldə edin

            for rejim in rejim_list:
                # Plan həcmini hesablamaq
                plan_hecmi = plan_hecmi_tarix_araligina_gore(plan_df, start_date, end_date, rejim)
                # Fakt həcmini hesablamaq
                fakt_hecmi = fakt_df[(fakt_df['Tarix'] >= pd.to_datetime(start_date)) & 
                                     (fakt_df['Tarix'] <= pd.to_datetime(end_date)) & 
                                     (fakt_df['Rejim'] == rejim)]['Həcm_fakt'].sum()

                                # Yerinə yetirmə faizini hesabla
                yerinə_yetirmə_faizi = (fakt_hecmi / plan_hecmi * 100) if plan_hecmi > 0 else 0
                data.append([rejim, plan_hecmi, fakt_hecmi, yerinə_yetirmə_faizi])

            # DataFrame yaradın
            results_df = pd.DataFrame(data, columns=['Rejim', 'Plan', 'Fakt', 'Yerinə yetirmə faizi'])

          
            create_table(results_df, "Rejimlər üzrə Plan və Fakt Həcmləri")

                     # Ekspeditorlar üzrə məlumatları toplamaq
            ekspeditorlar = plan_df['Ekspeditor'].unique()
            total_plan_hecmi_eksp = []
            total_fakt_hecmi_eksp = []

            # Tarix intervalına əsasən plan və fakt həcmlərini hesablayın
            for ekspeditor in ekspeditorlar:
                # Plan həcmini hesablamaq
                plan_hecmi_eksp = plan_hecmi_tarix_araligina_gore(plan_df[
                    (plan_df['Ekspeditor'] == ekspeditor) & 
                    (plan_df['Rejim'] == selected_rejim if selected_rejim != "Bütün rejimlər" else plan_df['Rejim'])], 
                    start_date, end_date)
                total_plan_hecmi_eksp.append(plan_hecmi_eksp)

                # Fakt həcmini hesablamaq
                fakt_hecmi_eksp = fakt_df[
                    (fakt_df['Tarix'] >= pd.to_datetime(start_date)) & 
                    (fakt_df['Tarix'] <= pd.to_datetime(end_date)) & 
                    (fakt_df['Eksp'] == ekspeditor) & 
                    (fakt_df['Rejim'] == selected_rejim if selected_rejim != "Bütün rejimlər" else fakt_df['Rejim'])
                ]['Həcm_fakt'].sum()
                total_fakt_hecmi_eksp.append(fakt_hecmi_eksp)

            # Ekspeditorların məlumatlarını cədvəl formatında göstərin
            ekspeditor_data = []
            total_fakt_hecmi_sum = sum(total_fakt_hecmi_eksp)  # Ümumi fakt həcmi

            for idx, ekspeditor in enumerate(ekspeditorlar):
                yerinə_yetirmə_faizi_eksp = (total_fakt_hecmi_eksp[idx] / total_plan_hecmi_eksp[idx] * 100) if total_plan_hecmi_eksp[idx] > 0 else 0
                
                # Daşınma payını hesabla
                dasinma_payi = (total_fakt_hecmi_eksp[idx] / total_fakt_hecmi_sum * 100) if total_fakt_hecmi_sum > 0 else 0
                
                ekspeditor_data.append([ekspeditor, total_plan_hecmi_eksp[idx], total_fakt_hecmi_eksp[idx], yerinə_yetirmə_faizi_eksp, dasinma_payi])

            # DataFrame yaradın
            ekspeditor_results_df = pd.DataFrame(ekspeditor_data, columns=['Ekspeditor', 'Plan', 'Fakt', 'Yerinə yetirmə faizi', 'Daşınma payı'])

            # Cədvəli göstərin
            create_table(ekspeditor_results_df.sort_values(by='Plan', ascending=False), "Ekspeditorlar üzrə Plan və Fakt Həcmləri")
