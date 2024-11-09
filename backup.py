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
    ("Report", "Rejimlər üzrə hesabat", "Digər yüklər", "Tranzit")
)

# Card tərzi üçün tərz
def card(title, value):
    st.markdown(f"""
        <div style="background-color: #e7e6eb; padding: 10px; border-radius: 10px; margin-bottom: 10px; text-align: center;">
            <p style="font-size: 24px; font-weight: bold; color: #302a6b; margin: 0;">{value}</p>
            <h3 style="margin: 3; font-size: 18px; padding-top: 10px; color: #302a6b;">{title}</h3>
        </div>
    """, unsafe_allow_html=True)

if page == "Rejimlər üzrə hesabat":
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
        st.warning("Zəhmət olmazsa tarix seçin.")
    else:
        if baslangic_tarix > bitis_tarix:
            st.error("Zəhmət olmazsa düzgün tarix aralığı seçin: Başlanğıc tarixi bitiş tarixindən əvvəl olmalıdır.")
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

            # İndeksi sıfırlayaraq sıralı indeks yaradın
            netice_df.reset_index(drop=True, inplace=True)
            # İndeksi 1-dən başlatmaq üçün
            netice_df.index = range(1, len(netice_df) + 1)

            # Yüklər üzrə cədvəli yaradın
            create_table(netice_df, "Yüklər üzrə plan və fakt həcmləri")






            import streamlit as st
            import pandas as pd
            import calendar

            # Tarix sütunlarını datetime formatına çevirmək
            fakt_df['Tarix'] = pd.to_datetime(fakt_df['Tarix'], errors='coerce')
            plan_df['Tarix'] = pd.to_datetime(plan_df['Tarix'], errors='coerce')

            # Tarix aralığına əsasən tam və qismən plan həcmi hesablayan funksiya
            def calculate_plan_hecmi(plan_df, start_date, end_date, rejim, yuk=None):
                country_plan_hecm = {}
                countries = plan_df['Göndərən ölkə'].unique()

                for country in countries:
                    total_plan_hecmi = 0

                    # Tam aylar üçün plan həcmini hesabla
                    for year in range(start_date.year, end_date.year + 1):
                        month_start = start_date.month if year == start_date.year else 1
                        month_end = end_date.month if year == end_date.year else 12

                        for month in range(month_start, month_end + 1):
                            if year == end_date.year and month == end_date.month:
                                break

                            monthly_plan = plan_df[
                                (plan_df['Tarix'].dt.year == year) &
                                (plan_df['Tarix'].dt.month == month) &
                                (plan_df['Rejim'] == rejim) &
                                (plan_df['Göndərən ölkə'] == country) &
                                (plan_df['Əsas yük'] == yuk)
                            ]['plan hecm'].sum()
                            total_plan_hecmi += monthly_plan

                    # Qismən ay üçün plan həcmini hesabla
                    days_in_end_month = calendar.monthrange(end_date.year, end_date.month)[1]
                    end_month_plan = plan_df[
                        (plan_df['Tarix'].dt.year == end_date.year) &
                        (plan_df['Tarix'].dt.month == end_date.month) &
                        (plan_df['Rejim'] == rejim) &
                        (plan_df['Göndərən ölkə'] == country) &
                        (plan_df['Əsas yük'] == yuk)
                    ]['plan hecm'].sum()

                    if end_month_plan > 0:
                        daily_plan_end_month = end_month_plan / days_in_end_month
                        partial_end_month_plan = daily_plan_end_month * end_date.day
                        total_plan_hecmi += partial_end_month_plan

                    country_plan_hecm[country] = total_plan_hecmi

                return country_plan_hecm

            ## Tranzit rejimində olan yüklər üzrə filter
            st.markdown("<h4 style='color: #e02020;'>Tranzit rejimində əsas yük göndərən ölkələr </h4>", unsafe_allow_html=True)

            # Tranzit rejimində olan yükləri filtrləmək və "Digər yüklər" seçimini çıxarmaq
            tranzit_yukler_df = fakt_df[(fakt_df['Rejim'] == 'Tranzit') & (fakt_df['əsas_yüklər'] != 'Digər yüklər')]['əsas_yüklər'].unique()

            # Tranzit rejimi üçün seçilə bilən yüklər filteri
            selected_yuk = st.selectbox("Tranzit rejimində əsas yükü seçin:", options=list(tranzit_yukler_df))


            # Plan həcmini hesablayırıq (yuxarıda təyin edilən `baslangic_tarix` və `bitis_tarix`-dən istifadə edirəm)
            if baslangic_tarix and bitis_tarix:
                tranzit_start_date = pd.to_datetime(baslangic_tarix)
                tranzit_end_date = pd.to_datetime(bitis_tarix)
                
                # Plan həcmini hesablayırıq
                country_plan_hecmi = calculate_plan_hecmi(plan_df, tranzit_start_date, tranzit_end_date, 'Tranzit', selected_yuk)

                # Fakt məlumatlarını hazırlamaq
                fakt_summary = fakt_df[
                    (fakt_df['Tarix'] >= tranzit_start_date) & 
                    (fakt_df['Tarix'] <= tranzit_end_date) & 
                    (fakt_df['Rejim'] == 'Tranzit') & 
                    (fakt_df['əsas_yüklər'] == selected_yuk)
                ].groupby('Göndərən ölkə')['Həcm_fakt'].sum().reset_index()

                # Plan məlumatlarını cədvələ çevirmək
                plan_df_summary = pd.DataFrame(list(country_plan_hecmi.items()), columns=['Göndərən ölkə', 'Hesablanmış Plan Həcmi'])

                # Plan və Fakt məlumatlarını birləşdir
                summary_df = pd.merge(
                    plan_df_summary, fakt_summary,
                    on='Göndərən ölkə', how='outer'
                ).fillna(0)

                # Yerinə yetirmə faizi hesablayın
                summary_df['Yerinə Yetirmə Faizi'] = summary_df.apply(
                    lambda row: (row['Həcm_fakt'] / row['Hesablanmış Plan Həcmi'] * 100) if row['Hesablanmış Plan Həcmi'] > 0 else 0,
                    axis=1
                )

                # Plan və fakt həcmi sıfır olanları çıxarırıq
                summary_df = summary_df[(summary_df['Hesablanmış Plan Həcmi'] != 0) | (summary_df['Həcm_fakt'] != 0)]

                # Cədvəli azalan sıraya görə düzün və indeks 1-dən başlasın
                summary_df = summary_df.sort_values(by='Hesablanmış Plan Həcmi', ascending=False).reset_index(drop=True)
                summary_df.index = range(1, len(summary_df) + 1)

                # Plan və fakt həcmi sıfır olanları çıxarırıq
                summary_df = summary_df[(summary_df['Hesablanmış Plan Həcmi'] != 0) | (summary_df['Həcm_fakt'] != 0)]

                # Cədvəl başlıqlarını dəyişərək stilizə edilmiş cədvəli göstərmək
                st.table(summary_df.rename(columns={
                    'Hesablanmış Plan Həcmi': 'Plan', 
                    'Həcm_fakt': 'Fakt', 
                    'Yerinə Yetirmə Faizi': 'Yerinə Yetirmə Faizi'
                }).style.format({
                    'Plan': '{:,.0f}',
                    'Fakt': '{:,.0f}',
                    'Yerinə Yetirmə Faizi': '{:.0f}%'
                }).set_table_styles([
                    {'selector': 'thead th', 'props': [('background-color', '#2b2563'), ('color', 'white')]},
                    {'selector': 'tbody td', 'props': [('text-align', 'center'), ('background-color', '#f0f0f5')]}
                ]))





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
            combined_df['Yerinə yetirmə faizi(Fraxt)'].fillna(0, inplace=False)

            # Plan və faktın boş olduğu ekspeditorları tapın
            fakt_ekspeditorlar = fakt_df['Eksp'].unique()
            plan_ekspeditorlar = plan_df['Ekspeditor'].unique()

            
           # "Plan(KM)" sütununa görə çoxdan aza sıralayın
            combined_df = combined_df.sort_values(by='Plan(KM)', ascending=False)

            # İndeksi sıfırlayaraq sıralı indeks yaradın
            combined_df.reset_index(drop=True, inplace=True)

            # İndeksi 1-dən başlatmaq üçün
            combined_df.index = range(1, len(combined_df) + 1)

            # Ekspeditorlar cədvəlini yaradın
            create_table(combined_df, "Ekspeditorlar üzrə plan və fakt həcmləri")
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

            
            # İndeksi sıfırlayaraq sıralı indeks yaradın
            vaqon_df.reset_index(drop=True, inplace=True)

            # İndeksi 1-dən başlatmaq üçün
            vaqon_df.index = range(1, len(vaqon_df) + 1)

            # Vaqon cədvəlini yaradın
            create_table(vaqon_df.sort_values(by='Plan', ascending=False), "Vaqon növü üzrə plan və fakt həcmləri")







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
        st.warning("Zəhmət olmazsa tarix seçin.")
    else:
        if baslangic_tarix > bitis_tarix:
            st.error("Zəhmət olmazsa düzgün tarix aralığı seçin: Başlanğıc tarixi bitiş tarixindən əvvəl olmalıdır.")
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

# İndeksi sıfırlayaraq sıralı indeks yaradın
            netice_df.reset_index(drop=True, inplace=True)
            # İndeksi 1-dən başlatmaq üçün
            netice_df.index = range(1, len(netice_df) + 1)


            # Yüklər üzrə cədvəli yaradın
            create_table(netice_df, "Yüklər üzrə plan və fakt həcmləri")
            # Digər yüklər üçün cardların yaradılması
           
            # Digər yüklər üçün cardların yaradılması
            if 'Digər yüklər' in netice_df['Yükün adı'].values:
                diger_yukler_row = netice_df[netice_df['Yükün adı'] == 'Digər yüklər'].iloc[0]
                
                # Digər yüklər üçün plan, fakt və yerinə yetirmə faizini əldə et
                diger_plan = diger_yukler_row['Plan']
                diger_fakt = diger_yukler_row['Fakt']
                diger_yerinə_yetirmə_faizi = diger_fakt / diger_plan * 100 if diger_plan > 0 else 0
 
                card_style = """
                <style>
                .card {
                    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
                    background-color: #e7e6eb;
                    border-radius: 5px;
                    padding: 10px;
                    margin-bottom: 15px;
                    text-align: center;
                    font-family: Arial, sans-serif;
                    font-size: 14px; /* Mətni kiçiltmək */
                    color: #302a6b;
                    height: 110px;  /* Card-ın hündürlüyünü təyin edir */
                }
                .card h1 {
                    font-size: 26px;  /* Başlığın ölçüsünü kiçiltmək */
                    color: #16105c;
                    margin-top: 10px; /* Başlığı kartın içində aşağıya doğru çəkir */
                    text-align: center; /* Başlığı mərkəzləşdirir */
                }
                .card p {
                    margin: 0; /* Başlığın altında heç bir boşluq qoymur */
                }
                </style>
                """

                st.markdown(card_style, unsafe_allow_html=True)

                # Cardları yan-yana göstərmək
                col1, col2, col3 = st.columns(3)

            with col1:
                card("Digər yüklər üzrə plan", f"{diger_plan:,.0f}")
            with col2:
                card("Digər yüklər üzrə fakt", f"{diger_fakt:,.0f}")
            with col3:
                card("Yerinə yetirmə faizi", f"{diger_yerinə_yetirmə_faizi:.0f}%")








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
            # İndeksi 1-dən başlatmaq üçün
            diger_yukler_grouped.index = range(1, len(diger_yukler_grouped) + 1)

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

    # Eyni tarixlər seçilibsə, ayın son gününü tapın
    if baslangic_tarix == bitis_tarix:
        month = baslangic_tarix.month
        year = baslangic_tarix.year
        days_in_month = ayin_gunleri_ve_hecmi(year, month)
        total_plan_hecmi += plan_df[(plan_df['Tarix'].dt.month == month) & (plan_df['Tarix'].dt.year == year)]['plan hecm'].sum() * (1 / days_in_month)
    else:
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
        total_plan_hecmi = plan_hecmi_tarix_araligina_gore(plan_df, start_date, end_date, selected_rejim)

        # Fakt həcmini hesablamaq
        total_fakt_hecmi = fakt_df[(fakt_df['Tarix'] >= pd.to_datetime(start_date)) & (fakt_df['Tarix'] <= pd.to_datetime(end_date))]['Həcm_fakt'].sum()

        # Yerinə yetirmə faizini hesabla
        yerinə_yetirmə_faizi_sum = (total_fakt_hecmi / total_plan_hecmi * 100) if total_plan_hecmi > 0 else 0

        # Cardları yan-yana göstərmək
        col1, col2, col3 = st.columns(3)

        # Bütün rejimlər üzrə toplam plan həcmini hesablamaq
        total_plan_hecmi_all = plan_hecmi_tarix_araligina_gore(plan_df, start_date, end_date)

        # Bütün rejimlər üzrə toplam fakt həcmini hesablamaq
        total_fakt_hecmi_all = fakt_df[(fakt_df['Tarix'] >= pd.to_datetime(start_date)) & 
                                        (fakt_df['Tarix'] <= pd.to_datetime(end_date))]['Həcm_fakt'].sum()

        # Yerinə yetirmə faizini hesabla
        yerinə_yetirmə_faizi_sum = (total_fakt_hecmi_all / total_plan_hecmi_all * 100) if total_plan_hecmi_all > 0 else 0

        # Card 1: Plan Həcmi
        with col1:
            st.markdown(f"""
                <div style="background-color:#e0e0e0; padding:10px; border-radius:8px; text-align:center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                    <h2 style='color: #30336b; margin: 0;'>{total_plan_hecmi_all:,.0f}</h2>
                    <p style='color: #30336b; margin: 0;'>Plan (ümumi)</p>
                </div>
            """, unsafe_allow_html=True)

        # Card 2: Fakt Həcmi
        with col2:
            st.markdown(f"""
                <div style="background-color:#e0e0e0; padding:10px; border-radius:8px; text-align:center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                    <h2 style='color: #30336b; margin: 0;'>{total_fakt_hecmi_all:,.0f}</h2>
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

            
            results_df = pd.DataFrame(data, columns=['Rejim', 'Plan', 'Fakt', 'Yerinə yetirmə faizi'])
            results_df = results_df.sort_values(by='Plan', ascending=False)
            # İndeksi sıfırlayaraq sıralı indeks yaradın
            results_df.reset_index(drop=True, inplace=True)

            # İndeksi 1-dən başlatmaq üçün
            results_df.index = range(1, len(results_df) + 1)

            # Cədvəli göstərin
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

            ekspeditor_results_df = ekspeditor_results_df.sort_values(by='Plan', ascending=False)

            # İndeksi sıfırlayaraq sıralı indeks yaradın
            ekspeditor_results_df.reset_index(drop=True, inplace=True)

            # İndeksi 1-dən başlatmaq üçün
            ekspeditor_results_df.index = range(1, len(ekspeditor_results_df) + 1)

            # Cədvəli göstərin
            create_table(ekspeditor_results_df, "Ekspeditorlar üzrə Plan və Fakt Həcmləri")


import streamlit as st
import pandas as pd
import calendar
import datetime

# Məlumatların yüklənməsi və tarix formatına çevrilməsi
fakt_df['Tarix'] = pd.to_datetime(fakt_df['Tarix'], errors='coerce')
plan_df['Tarix'] = pd.to_datetime(plan_df['Tarix'], errors='coerce')

# Tranzit səhifəsi
if page == "Tranzit":

    st.markdown(
    """
    <h1 style='text-align: center; color: #2b2563; font-size: 30px; font-weight: bold;'>
    Tranzit rejimdə mənşə ölkələr üzrə daşınma statistikası
    </h1>
    """,
    unsafe_allow_html=True
)


    # Tarix filtrlərini yaratmaq üçün iki sütun istifadə edirik
    col_start_date, col_end_date = st.columns(2)

    # Başlanğıc tarixi üçün giriş
    with col_start_date:
        tranzit_start_date = st.date_input(
            "Başlanğıc tarixi",
            value=datetime.date(2024, 1, 1),
            min_value=datetime.date(2023, 1, 1),
            max_value=datetime.date.today()
        )

    # Bitiş tarixi üçün giriş
    with col_end_date:
        tranzit_end_date = st.date_input(
            "Bitiş tarixi",
            value=datetime.date.today(),
            min_value=tranzit_start_date,
            max_value=datetime.date.today()
        )

    if tranzit_start_date and tranzit_end_date:
        tranzit_start_date = pd.to_datetime(tranzit_start_date)
        tranzit_end_date = pd.to_datetime(tranzit_end_date)

        # Tarix aralığına əsasən tam və qismən plan həcmi hesablayan funksiya
        def calculate_plan_hecmi(plan_df, start_date, end_date, rejim):
            country_plan_hecm = {}
            countries = plan_df['Göndərən ölkə'].unique()

            for country in countries:
                total_plan_hecmi = 0

                # Tam aylar üçün plan həcmini hesabla
                for year in range(start_date.year, end_date.year + 1):
                    month_start = start_date.month if year == start_date.year else 1
                    month_end = end_date.month if year == end_date.year else 12

                    for month in range(month_start, month_end + 1):
                        # Son ay üçün çıxış
                        if year == end_date.year and month == end_date.month:
                            break

                        # Tam ay üçün plan həcmi
                        monthly_plan = plan_df[
                            (plan_df['Tarix'].dt.year == year) &
                            (plan_df['Tarix'].dt.month == month) &
                            (plan_df['Rejim'] == rejim) &
                            (plan_df['Göndərən ölkə'] == country) &
                            (plan_df['Əsas yük'] != 'Digər yüklər')
                        ]['plan hecm'].sum()
                        total_plan_hecmi += monthly_plan

                # Qismən ay üçün plan həcmi
                days_in_end_month = calendar.monthrange(end_date.year, end_date.month)[1]
                end_month_plan = plan_df[
                    (plan_df['Tarix'].dt.year == end_date.year) &
                    (plan_df['Tarix'].dt.month == end_date.month) &
                    (plan_df['Rejim'] == rejim) &
                    (plan_df['Göndərən ölkə'] == country) &
                    (plan_df['Əsas yük'] != 'Digər yüklər')
                ]['plan hecm'].sum()

                if end_month_plan > 0:
                    daily_plan_end_month = end_month_plan / days_in_end_month
                    partial_end_month_plan = daily_plan_end_month * end_date.day
                    total_plan_hecmi += partial_end_month_plan

                country_plan_hecm[country] = total_plan_hecmi

            return country_plan_hecm

        # Plan həcmini hesablayırıq
        country_plan_hecmi = calculate_plan_hecmi(plan_df, tranzit_start_date, tranzit_end_date, 'Tranzit')

        # Fakt məlumatlarını hazırlamaq (Digər yüklər çıxarılır)
        fakt_summary = fakt_df[
            (fakt_df['Tarix'] >= tranzit_start_date) &
            (fakt_df['Tarix'] <= tranzit_end_date) &
            (fakt_df['Rejim'] == 'Tranzit') &
            (fakt_df['əsas_yüklər'] != 'Digər yüklər')
        ].groupby('Göndərən ölkə')['Həcm_fakt'].sum().reset_index()

        # Plan məlumatlarını cədvələ çevirmək
        plan_df_summary = pd.DataFrame(list(country_plan_hecmi.items()), columns=['Göndərən ölkə', 'Hesablanmış Plan Həcmi'])

        # Plan və Fakt məlumatlarını birləşdir
        summary_df = pd.merge(
            plan_df_summary, fakt_summary,
            on='Göndərən ölkə', how='outer'
        ).fillna(0)


        # Azərbaycan adını "Digər" ilə əvəz edirik
        summary_df['Göndərən ölkə'] = summary_df['Göndərən ölkə'].replace('Azərbaycan', 'Digər')

        # Yerinə yetirmə faizini hesablayın
        summary_df['Yerinə Yetirmə Faizi'] = summary_df.apply(
            lambda row: (row['Həcm_fakt'] / row['Hesablanmış Plan Həcmi'] * 100) if row['Hesablanmış Plan Həcmi'] > 0 else 0,
            axis=1
        )

        # Plan və fakt həcmi sıfır olanları çıxarırıq
        summary_df = summary_df[(summary_df['Hesablanmış Plan Həcmi'] != 0) | (summary_df['Həcm_fakt'] != 0)]

        # Cədvəli azalan sıraya görə düzün və indeks 1-dən başlasın
        summary_df = summary_df.sort_values(by='Hesablanmış Plan Həcmi', ascending=False).reset_index(drop=True)
        summary_df.index = range(1, len(summary_df) + 1)

        

        st.table(summary_df.style.format({
            'Hesablanmış Plan Həcmi': '{:,.0f}',
            'Həcm_fakt': '{:,.0f}',
            'Yerinə Yetirmə Faizi': '{:.0f}%'
        }).set_table_styles([
            {'selector': 'thead th', 'props': [('background-color', '#2b2563'), ('color', 'white')]},
            {'selector': 'tbody td', 'props': [('text-align', 'center'), ('background-color', '#f0f0f5')]}
        ]))


        
        # Hər yük üzrə tam və qismən plan həcmini hesablayan funksiya
        def calculate_plan_hecmi(plan_df, start_date, end_date, rejim, country, yuk):
            total_plan_hecmi = 0

            # Tam aylar üçün plan həcmini hesabla
            for year in range(start_date.year, end_date.year + 1):
                month_start = start_date.month if year == start_date.year else 1
                month_end = end_date.month if year == end_date.year else 12

                for month in range(month_start, month_end + 1):
                    days_in_month = calendar.monthrange(year, month)[1]

                    # Tam ay üçün plan həcmi
                    monthly_plan = plan_df[
                        (plan_df['Tarix'].dt.year == year) &
                        (plan_df['Tarix'].dt.month == month) &
                        (plan_df['Rejim'] == rejim) &
                        (plan_df['Göndərən ölkə'] == country) &
                        (plan_df['Əsas yük'] == yuk)
                    ]['plan hecm'].sum()
                    
                    if monthly_plan > 0:
                        if year == end_date.year and month == end_date.month:
                            # Qismən ay üçün hesabla
                            partial_days = end_date.day
                            total_plan_hecmi += (monthly_plan / days_in_month) * partial_days
                        elif year == start_date.year and month == start_date.month:
                            # Başlanğıc ayı qismən hesabla
                            partial_days = days_in_month - start_date.day + 1
                            total_plan_hecmi += (monthly_plan / days_in_month) * partial_days
                        else:
                            # Tam ay üçün hesabla
                            total_plan_hecmi += monthly_plan

            return total_plan_hecmi

        # Göndərən ölkələr üzrə filter
        st.markdown("<h4 style='color: #2b2563;'>Göndərən ölkə</h4>", unsafe_allow_html=True)
        available_countries = fakt_df['Göndərən ölkə'].unique()
        selected_country = st.selectbox("Göndərən ölkəni seçin:", options=available_countries)

        # Fakt məlumatlarını hazırlamaq (Digər yüklər çıxarılır)
        fakt_summary = fakt_df[
            (fakt_df['Tarix'] >= tranzit_start_date) &
            (fakt_df['Tarix'] <= tranzit_end_date) &
            (fakt_df['Rejim'] == 'Tranzit') &
            (fakt_df['Göndərən ölkə'] == selected_country) &
            (fakt_df['əsas_yüklər'] != 'Digər yüklər')
        ].groupby('əsas_yüklər')['Həcm_fakt'].sum().reset_index()

        # Yüklər üzrə plan məlumatlarını hesablamaq
        yukler = fakt_summary['əsas_yüklər'].unique()
        yuk_plan_hecmi = []
        yuk_fakt_hecmi = []

        for yuk in yukler:
            plan_hecmi = calculate_plan_hecmi(plan_df, tranzit_start_date, tranzit_end_date, 'Tranzit', selected_country, yuk)
            fakt_hecmi = fakt_summary[fakt_summary['əsas_yüklər'] == yuk]['Həcm_fakt'].sum()
            yuk_plan_hecmi.append(plan_hecmi)
            yuk_fakt_hecmi.append(fakt_hecmi)

        # Plan və fakt məlumatlarını birləşdirmək
        summary_yuk_df = pd.DataFrame({
            'Yükün adı': yukler,
            'Plan': yuk_plan_hecmi,
            'Fakt': yuk_fakt_hecmi
        })

        summary_yuk_df['Yerinə Yetirmə Faizi'] = summary_yuk_df.apply(
            lambda row: (row['Fakt'] / row['Plan'] * 100) if row['Plan'] > 0 else 0,
            axis=1
        )

        # Plan və fakt həcmi sıfır olanları çıxarırıq
        summary_yuk_df = summary_yuk_df[(summary_yuk_df['Plan'] != 0) | (summary_yuk_df['Fakt'] != 0)]

        # Cədvəli azalan sıraya görə düzün və indeks 1-dən başlasın
        summary_yuk_df = summary_yuk_df.sort_values(by='Plan', ascending=False).reset_index(drop=True)
        summary_yuk_df.index = range(1, len(summary_yuk_df) + 1)

        # Stilizə olunmuş cədvəli göstərmək
        
        st.table(summary_yuk_df[['Yükün adı', 'Plan', 'Fakt', 'Yerinə Yetirmə Faizi']].style.format({
            'Plan': '{:,.0f}',
            'Fakt': '{:,.0f}',
            'Yerinə yetirmə Faizi': '{:.0f}%'
        }).set_table_styles([
            {'selector': 'thead th', 'props': [('background-color', '#2b2563'), ('color', 'white')]},
            {'selector': 'tbody td', 'props': [('text-align', 'center'), ('background-color', '#f0f0f5')]}
        ]))
