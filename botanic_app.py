import streamlit as st
import math, random
import matplotlib.pyplot as plt

st.set_page_config(page_title="Relevés botaniques", layout="centered")
st.title("🌿 Application de relevés botaniques")

# --- Étape 0 : numéro du relevé ---
st.header("0️⃣ Numéro du relevé")
numero_releve = st.text_input("Entrez le numéro du relevé :", "")

# --- Étape 1 : Paramètres de la zone ---
st.header("1️⃣ Paramètres de la zone")
forme = st.radio("Choisissez une forme :", ["Quadrilatère", "Cercle"])
if forme == "Quadrilatère":
    longueur = st.number_input("Longueur (m)", min_value=1.0, value=10.0, step=1.0)
    largeur = st.number_input("Largeur (m)", min_value=1.0, value=5.0, step=1.0)
    surface = longueur * largeur
else:
    diametre = st.number_input("Diamètre (m)", min_value=1.0, value=10.0, step=1.0)
    surface = math.pi * (diametre/2)**2

densite = st.number_input("Densité de points (points / m²)",
                          min_value=0.001, value=0.1, step=0.01,
                          help="0.1 = 1 point pour 10 m²")
nb_points = max(1, int(surface * densite))

st.write(f"Surface estimée : **{surface:.2f} m²**")
st.write(f"Nombre de points à générer : **{nb_points}**")

# --- Génération des points ---
if st.button("🎲 Générer les points d'observation"):
    points = []
    if forme == "Quadrilatère":
        for _ in range(nb_points):
            x = random.uniform(0, longueur)
            y = random.uniform(0, largeur)
            points.append((x, y))
    else:
        r = diametre / 2
        for _ in range(nb_points):
            while True:
                x = random.uniform(-r, r)
                y = random.uniform(-r, r)
                if x**2 + y**2 <= r**2:
                    points.append((x, y))
                    break
    st.session_state["points"] = points
    st.session_state["visited"] = [False]*len(points)
    st.session_state["current"] = None
    st.success("Points générés !")

# --- Affichage visuel ---
if "points" in st.session_state:
    points = st.session_state["points"]

    st.header("🗺️ Carte des points")
    fig, ax = plt.subplots()
    xs, ys = zip(*points)
    ax.scatter(xs, ys, c="green", s=50)  # points plus petits
    # ajouter les numéros sur chaque point
    for i, (x, y) in enumerate(points):
        ax.text(x, y, str(i), fontsize=8, ha='center', va='bottom', color='black')

    # point de départ
    ax.scatter(0, 0, c="red", marker="x", s=100)
    ax.set_aspect("equal", adjustable="box")
    if forme == "Quadrilatère":
        ax.set_xlim(-1, longueur + 1)
        ax.set_ylim(-1, largeur + 1)
        title = "Quadrilatère"
    else:
        r = diametre / 2
        circle = plt.Circle((0, 0), r, color="blue", fill=False)
        ax.add_patch(circle)
        ax.set_xlim(-r - 1, r + 1)
        ax.set_ylim(-r - 1, r + 1)
        title = "Cercle"
    ax.set_title(title)
    st.pyplot(fig)
    st.caption("Points verts : observations. Point rouge : départ. Numéros sur les points.")

    # --- Sélection du point ---
    visited = st.session_state["visited"]
    remaining = [(i, p) for i, p in enumerate(points) if not visited[i]]
    if remaining:
        index = st.selectbox("Choisissez un point à rejoindre :", [i for i, _ in remaining])
        point = points[index]

        # Slider pour simuler distance parcourue (0=start, distance=fin)
        dx = point[0] - 0
        dy = point[1] - 0
        distance_totale = math.sqrt(dx**2 + dy**2)
        avance = st.slider("Distance parcourue depuis le départ (m)", 0.0, distance_totale, 0.0, step=0.1)
        distance_restante = distance_totale - avance

        # Calcul angle flèche
        angle_rad = math.atan2(dy, dx)
        angle_deg = (math.degrees(angle_rad) + 360) % 360

        st.markdown(f"<h1 style='text-align:center;color:green;'>{distance_restante:.2f} m</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center;'>&#8593;</h2>", unsafe_allow_html=True)  # flèche vers le haut (placeholder)
        st.write("La flèche devrait être orientée dynamiquement vers le point (simulation avec angle ici).")

        if st.button("✅ Marquer comme visité et saisir les espèces"):
            st.session_state["current"] = index

# --- Saisie des espèces ---
if "current" in st.session_state and st.session_state["current"] is not None:
    idx = st.session_state["current"]
    st.header(f"3️⃣ Saisie des espèces pour le point {idx}")
    especes = st.text_area("Liste des espèces observées (une par ligne)")
    if st.button("💾 Enregistrer ce point"):
        visited = st.session_state["visited"]
        visited[idx] = True
        st.session_state["visited"] = visited
        if "data" not in st.session_state:
            st.session_state["data"] = {}
        st.session_state["data"][idx] = especes.splitlines()
        st.session_state["current"] = None
        st.success("Espèces enregistrées. Retournez au point de départ puis choisissez un nouveau point.")

# --- Résumé ---
if "data" in st.session_state and st.session_state["data"]:
    st.header("📋 Résumé des relevés")
    for idx, species in st.session_state["data"].items():
        st.write(f"**Point {idx}** : {', '.join(species) if species else 'Aucune espèce saisie'}")
