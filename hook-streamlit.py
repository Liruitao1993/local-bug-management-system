# Streamlit应用PyInstaller钩子文件
# 用于处理Streamlit应用的特殊导入需求

from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

# 收集Streamlit相关的所有模块和数据
datas, binaries, hiddenimports = collect_all('streamlit')

# 额外的隐含导入
hiddenimports += [
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner.script_runner',
    'streamlit.runtime.state',
    'streamlit.runtime.secrets',
    'streamlit.runtime.caching',
    'streamlit.runtime.media_file_manager',
    'streamlit.components.v1',
    'streamlit.elements',
    'streamlit.elements.form',
    'streamlit.elements.widgets',
    'pandas._libs.tslibs.base',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.timestamps',
    'plotly.graph_objects._figure',
    'plotly.validators',
    'plotly.validators.scatter',
    'openpyxl.cell._writer',
]

# 收集额外的数据文件
datas += collect_data_files('streamlit')
datas += collect_data_files('plotly')
datas += collect_data_files('pandas')