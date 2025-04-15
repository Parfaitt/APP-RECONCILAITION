def metric_card(title, value, color, icon=None):
    if icon:
        title = f"{icon} {title}"
    return f"""
    <div style="
        border-radius: 10px;
        padding: 15px;
        background-color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-left: 5px solid {color};
        height: 120px;
        min-width: 200px;  /* Largeur minimale garantie */
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow: hidden;  /* Empêche le débordement */
    ">
        <h3 style="
            color: #555; 
            font-size: 16px; 
            margin: 0 0 8px 0;
            font-weight: normal;
            white-space: nowrap;  /* Empêche le retour à la ligne */
        ">{title}</h3>
        <p style="
            color: #222; 
            font-size: 15px;  /* Taille réduite pour les grands nombres */
            font-weight: bold; 
            margin: 0;
            font-family: 'Courier New', monospace;
            word-break: break-all;  /* Gestion des mots longs */
            line-height: 1.2;
        ">{value}</p>
    </div>
    """