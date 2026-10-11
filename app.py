        elif st.session_state.asset_type == "Fondos indexados":
            st.markdown("### 🔍 Buscador Inteligente en Tiempo Real de Fondos Indexados")
            fund_query = st.text_input("Escribe una palabra clave, nombre o ISIN (ej. 'vanguard', 'msci world', 'IE00B03HD191'):", value=default_input).strip()
            
            user_input = ""
            if fund_query:
                with st.spinner(f"Buscando '{fund_query}' en la base de fondos..."):
                    try:
                        results = yf.Search(fund_query, max_results=8).quotes
                        fund_results = [r for r in results if r.get('quoteType') == 'MUTUALFUND' or 'FUND' in r.get('longname', '').upper() or 'INDEX' in r.get('longname', '').upper()]
                        
                        if not fund_results:
                            fund_results = results

                        if fund_results:
                            st.success(f"¡Se han encontrado {len(fund_results)} resultados en tiempo real!")
                            options_map = {f"{item.get('shortname', item.get('longname', ''))} ({item.get('symbol', '')}) - [{item.get('exchange', '')}]": item.get('symbol') for item in fund_results}
                            selected_label = st.selectbox("Selecciona el Fondo de la lista en tiempo real:", options=["-- Selecciona un resultado --"] + list(options_map.keys()))
                            
                            if not selected_label.startswith("--"):
                                user_input = options_map[selected_label]
                        else:
                            st.warning("No se encontraron resultados automáticos. Usaremos el texto introducido directamente.")
                            user_input = fund_query
                    except Exception as e:
                        st.error(f"Error en la búsqueda en tiempo real: {e}")
                        user_input = fund_query
