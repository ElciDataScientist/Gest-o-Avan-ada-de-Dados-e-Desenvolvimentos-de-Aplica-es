from tarfile import data_filter
import pandas            as pd
import streamlit         as st
import seaborn           as sns
import numpy             as np
import plotly.express    as px
import matplotlib.pyplot as plt
from PIL                 import Image
from io                  import BytesIO

# Configurações personalizadas para melhorar o visual dos plots
custom_params = {
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.grid": True,
    "grid.color": "lightgrey",
    "grid.linestyle": ":",
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans", "Bitstream Vera Sans", "sans-serif"],
    "lines.linewidth": 2,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "legend.frameon": False,
    "figure.figsize": (10, 6),
    "axes.titlesize": 14
}
# Aplicar o tema e as configurações personalizadas
sns.set_theme(style="whitegrid", palette="deep", rc=custom_params)

# Configuração adicional para o estilo dos plots
plt.rcParams['axes.axisbelow'] = True
plt.rcParams['axes.edgecolor'] = 'lightgrey'



# Função para ler os dados
@st.cache_data(show_spinner=True)
def load_data(file_data):
    """
    Carrega os dados de um arquivo CSV ou Excel e armazena em cache.
    
    Parâmetros:
    file_data: Arquivo carregado (pode ser um objeto UploadedFile do Streamlit ou um caminho de arquivo).
    
    Retorna:
    pandas.DataFrame: DataFrame contendo os dados do arquivo.
    """
    try:
        # Tenta ler como CSV primeiro
        return pd.read_csv(file_data, sep=';')
    except Exception as csv_error:
        try:
            # Se falhar, tenta ler como Excel
            return pd.read_excel(file_data)
        except Exception as excel_error:
            st.error(f"Erro ao carregar o arquivo CSV: {str(csv_error)}")
            st.error(f"Erro ao carregar o arquivo Excel: {str(excel_error)}")
            return None
        

# Função para filtrar baseado na multiseleção de categorias
@st.cache_data
def multiselect_filter(relatorio, col, selecionados):
    """
    Filtra um DataFrame baseado na multiseleção de categorias.
    
    Parâmetros:
    relatorio (pd.DataFrame): O DataFrame a ser filtrado.
    col (str): O nome da coluna a ser usada para filtragem.
    selecionados (list): Lista de categorias selecionadas.
    
    Retorna:
    pd.DataFrame: DataFrame filtrado.
    """
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True) 
    
    
# Função para converter o df para csv
@st.cache_data
def convert_df(df):
    """
    Converte um DataFrame para CSV.
    
    Parâmetros:
    df (pd.DataFrame): O DataFrame a ser convertido.
    
    Retorna:
    bytes: O conteúdo do CSV codificado em UTF-8.
    """
    return df.to_csv(index=False).encode('utf-8')       


# Função para converter o df para excel
@st.cache_data
def to_excel(df):
    """
    Converte um DataFrame para Excel.
    
    Parâmetros:
    df (pd.DataFrame): O DataFrame a ser convertido.
    
    Retorna:
    bytes: O conteúdo do arquivo Excel.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    processed_data = output.getvalue()
    return processed_data


# Função principal da aplicação
def main():
    # Configuração inicial da página da aplicação
    st.set_page_config(
        page_title='Telemarketing Analysis',
        page_icon='telmarketing_icon.png',
        layout="wide",
        initial_sidebar_state='expanded'
    )

    # Título principal da aplicação
    st.title('Analise do TeleMarketing')
    st.markdown("---")
    
    # Apresenta a imagem na barra lateral da aplicação
    image = Image.open("Bank-Branding.jpg")
    st.sidebar.image(image)

    # Botão para carregar arquivo na aplicação
    st.sidebar.header("Upload do arquivo")
    data_file_1 = st.sidebar.file_uploader("Bank Marketing Data", type=['csv', 'xlsx'])

    # Verifica se há conteúdo carregado na aplicação
    if data_file_1 is not None:
        bank_raw = load_data(data_file_1)
        bank = bank_raw.copy()

        st.header('Dados antes dos filtros')
        st.dataframe(bank_raw.head())

        with st.sidebar.form(key='my_form'):
            st.header("Filtros")

            # SELECIONA O TIPO DE GRÁFICO
            graph_type = st.radio('Tipo de gráfico:', ('Barras', 'Pizza'))
        
            # IDADES
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider('Idade', 
                               min_value=min_age,
                               max_value=max_age, 
                               value=(min_age, max_age),
                               step=1)

            # PROFISSÕES
            jobs_list = ['all'] + bank.job.unique().tolist()
            jobs_selected = st.multiselect("Profissão", jobs_list, ['all'])

            # ESTADO CIVIL
            marital_list = ['all'] + bank.marital.unique().tolist()
            marital_selected = st.multiselect("Estado civil", marital_list, ['all'])

            # DEFAULT?
            default_list = ['all'] + bank.default.unique().tolist()
            default_selected = st.multiselect("Default", default_list, ['all'])

            # TEM FINANCIAMENTO IMOBILIÁRIO?
            housing_list = ['all'] + bank.housing.unique().tolist()
            housing_selected = st.multiselect("Tem financiamento imob?", housing_list, ['all'])

            # TEM EMPRÉSTIMO?
            loan_list = ['all'] + bank.loan.unique().tolist()
            loan_selected = st.multiselect("Tem empréstimo?", loan_list, ['all'])

            # MEIO DE CONTATO?
            contact_list = ['all'] + bank.contact.unique().tolist()
            contact_selected = st.multiselect("Meio de contato", contact_list, ['all'])

            # MÊS DO CONTATO
            month_list = ['all'] + bank.month.unique().tolist()
            month_selected = st.multiselect("Mês do contato", month_list, ['all'])

            # DIA DA SEMANA
            day_of_week_list = ['all'] + bank.day_of_week.unique().tolist()
            day_of_week_selected = st.multiselect("Dia da semana", day_of_week_list, ['all'])

            submit_button = st.form_submit_button(label='Aplicar')

        if submit_button:
            # encadeamento de métodos para filtrar a seleção
            bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                        .pipe(multiselect_filter, 'job', jobs_selected)
                        .pipe(multiselect_filter, 'marital', marital_selected)
                        .pipe(multiselect_filter, 'default', default_selected)
                        .pipe(multiselect_filter, 'housing', housing_selected)
                        .pipe(multiselect_filter, 'loan', loan_selected)
                        .pipe(multiselect_filter, 'contact', contact_selected)
                        .pipe(multiselect_filter, 'month', month_selected)
                        .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
            )

            st.header('Dados após os filtros')
            st.dataframe(bank.head())


    else:
        st.info('Aguardando o upload do arquivo CSV.')

if __name__ == "__main__":
    main() 
       
def main():
    st.title("Aplicação com Dados Persistentes")

    # Botão para carregar arquivo na aplicação
    st.sidebar.header("Upload do arquivo")
    data_file_1 = st.sidebar.file_uploader("Bank Marketing", type=['csv', 'xlsx'])
    
    if data_file_1 is not None:
        bank_raw = load_data(data_file_1)
        if bank_raw is not None:
            # ... (código de filtragem permanece o mesmo)

            # Cálculo das proporções
            bank_raw_target_perc = bank_raw.y.value_counts(normalize=True).to_frame() * 100
            bank_raw_target_perc = bank_raw_target_perc.sort_index()
            
            try:
                bank_target_perc = bank.y.value_counts(normalize=True).to_frame() * 100
                bank_target_perc = bank_target_perc.sort_index()
            except:
                st.error('Erro no filtro')
                return

            # Botões de download dos dados dos gráficos
            col1, col2 = st.columns(2)

            df_xlsx = to_excel(bank_raw_target_perc)
            col1.write('### Proporção original')
            col1.write(bank_raw_target_perc)
            col1.download_button(label='📥 Download',
                                data=df_xlsx,
                                file_name='bank_raw_y.xlsx',
                                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            
            df_xlsx = to_excel(bank_target_perc)
            col2.write('### Proporção da tabela com filtros')
            col2.write(bank_target_perc)
            col2.download_button(label='📥 Download',
                                data=df_xlsx,
                                file_name='bank_y.xlsx',
                                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            st.markdown("---")

            st.write('## Proporção de aceite')
            # PLOTS    
            fig, ax = plt.subplots(1, 2, figsize=(12, 5))

            if graph_type == 'Barras':
                sns.barplot(x=bank_raw_target_perc.index, 
                            y='y',
                            data=bank_raw_target_perc, 
                            ax=ax[0])
                ax[0].bar_label(ax[0].containers[0])
                ax[0].set_title('Dados brutos',
                                fontweight="bold")
                
                sns.barplot(x=bank_target_perc.index, 
                            y='y', 
                            data=bank_target_perc, 
                            ax=ax[1])
                ax[1].bar_label(ax[1].containers[0])
                ax[1].set_title('Dados filtrados',
                                fontweight="bold")
            else:
                bank_raw_target_perc.plot(kind='pie', autopct='%.2f', y='y', ax=ax[0])
                ax[0].set_title('Dados brutos',
                                fontweight="bold")
                
                bank_target_perc.plot(kind='pie', autopct='%.2f', y='y', ax=ax[1])
                ax[1].set_title('Dados filtrados',
                                fontweight="bold")

            st.pyplot(fig)

            # Opção para baixar o gráfico
            buf = BytesIO()
            fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
            st.download_button(
                label="📥 Download Gráfico",
                data=buf.getvalue(),
                file_name=f"grafico_{graph_type.lower()}.png",
                mime="image/png",
            )

if __name__ == '__main__':
    main()
        
        


    
    