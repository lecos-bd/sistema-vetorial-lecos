import numpy as np
import plotly.graph_objects as go
import data as dt

df_ambiental = dt.tratamento_ambiental()
df_seguranca = dt.tratamento_seguranca()
df_equidade = dt.tratamento_equidade()

def gerar_grafico(estado, ano):
    # Filtrar os dados
    df_ambiental_filt = df_ambiental[(df_ambiental['Estado'] == estado) & (df_ambiental['Ano'] == ano)]
    df_seguranca_filt = df_seguranca[(df_seguranca['Estado'] == estado) & (df_seguranca['Ano'] == ano)]
    df_equidade_filt = df_equidade[(df_equidade['Estado'] == estado) & (df_equidade['Ano'] == ano)]

    # Somar e tratar valores nulos
    equidade = df_equidade_filt['Escala'].sum() or 0
    ambiental = df_ambiental_filt['Escala'].sum() or 0
    seguranca = df_seguranca_filt['Escala'].sum() or 0

    # Verificação de depuração
    print(f"[gerar_grafico] {estado=} {ano=} => E:{equidade}, S:{seguranca}, A:{ambiental}")

    # Vetores
    start = [0, 0, 0]
    ideal = [10, 10, 10]
    gen = [equidade, seguranca, ambiental]

    fig = go.Figure()

    # Vetores principais
    fig.add_trace(go.Scatter3d(
        x=[0, gen[0]], y=[0, gen[1]], z=[0, gen[2]],
        mode='lines+markers', line=dict(color='red', width=5),
        marker=dict(size=4), name='Vetor do Trilema do Estado'))

    fig.add_trace(go.Scatter3d(
        x=[0, ideal[0]], y=[0, ideal[1]], z=[0, ideal[2]],
        mode='lines+markers', line=dict(color='blue', width=5),
        marker=dict(size=4), name='Vetor do Trilema Ideal'))

    # Projeções - estado
    fig.add_trace(go.Scatter3d(x=[0, gen[0]], y=[0, 0], z=[0, 0], line=dict(color='#ffba08', width=5), mode='lines+markers', marker=dict(size=4), name='Equidade Estado'))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, gen[1]], z=[0, 0], line=dict(color='#ffba08', width=5), mode='lines+markers', marker=dict(size=4), name='Segurança Estado'))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, gen[2]], line=dict(color='#ffba08', width=5), mode='lines+markers', marker=dict(size=4), name='Ambiental Estado'))

    # Projeções - ideal
    fig.add_trace(go.Scatter3d(x=[0, ideal[0]], y=[0, 0], z=[0, 0], line=dict(color='#1d3557', width=5), mode='lines+markers', marker=dict(size=4), name='Equidade Ideal'))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, ideal[1]], z=[0, 0], line=dict(color='#1d3557', width=5), mode='lines+markers', marker=dict(size=4), name='Segurança Ideal'))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, ideal[2]], line=dict(color='#1d3557', width=5), mode='lines+markers', marker=dict(size=4), name='Ambiental Ideal'))

    # Superfícies
    def extrair_v(v): return ([v[0], 0, 0], [0, v[1], 0], [0, 0, v[2]])
    def xyz(vlist): return [list(coord) for coord in zip(*vlist)]

    for v, cor in [(gen, 'red'), (ideal, 'lightblue')]:
        pts = extrair_v(v)
        x, y, z = xyz(pts)
        fig.add_trace(go.Mesh3d(x=x, y=y, z=z, i=[0], j=[1], k=[2], opacity=0.5, color=cor))

    # Layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[0, 10], title='Equity - x'),
            yaxis=dict(range=[0, 10], title='Security - y'),
            zaxis=dict(range=[0, 10], title='Environmental - z'),
            bgcolor="rgba(0,0,0,0)"
        ),
        title=f"Vetores 3D: {estado} - {ano}",
        height=700,
        width=820
    )

    # Função para calcular ângulo entre vetores
    def angulo(v1, v2):
        v1, v2 = np.array(v1), np.array(v2)
        return np.degrees(np.arccos(np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)), -1.0, 1.0)))

    eixo_x, eixo_y, eixo_z = [1,0,0], [0,1,0], [0,0,1]

    return fig.to_html(full_html=False, include_plotlyjs='cdn'), {
        "angulo_ideal_x": f"Eixo X: {angulo(ideal, eixo_x):.2f}°",
        "angulo_ideal_y": f"Eixo Y: {angulo(ideal, eixo_y):.2f}°",
        "angulo_ideal_z": f"Eixo Z: {angulo(ideal, eixo_z):.2f}°",
        "angulo_generico_x": f"Eixo X: {angulo(gen, eixo_x):.2f}°",
        "angulo_generico_y": f"Eixo Y: {angulo(gen, eixo_y):.2f}°",
        "angulo_generico_z": f"Eixo Z: {angulo(gen, eixo_z):.2f}°",
        "angulo_generico_ideal": f"Angulo entre vetor genérico e ideal: {angulo(ideal, gen):.2f}°",
        "angulo_ambiental_seguranca": f"Ambiental e segurança: {np.degrees(np.arctan2(ambiental, seguranca)):.2f}°",
        "angulo_ambiental_equidade": f"Ambiental e equidade: {np.degrees(np.arctan2(ambiental, equidade)):.2f}°",
        "angulo_seguranca_equidade": f"Segurança e equidade: {np.degrees(np.arctan2(seguranca, equidade)):.2f}°",
    }
