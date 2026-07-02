import json

class controlador:
    def __init__(self):
        # Guardamos el estado del ciclo anterior para comparar
        self.datos_anterior = {}
        self.datos_actual = {}

    def recibir_datos(self, datos):
        """Punto de entrada. Retorna el estado global de cada proceso."""
        if not self.datos_anterior:
            # En el primer ciclo no hay con qué comparar, guardamos y asumimos normalidad
            self.datos_anterior = datos
            return "NORMAL", "NORMAL"
        
        self.datos_actual = datos
        
        estado_agua = "NORMAL"
        estado_salmuera = "NORMAL"

        if "server_agua" in self.datos_actual and "server_agua" in self.datos_anterior:
            estado_agua = self.evaluar_datos_agua(
                self.datos_actual["server_agua"], 
                self.datos_anterior["server_agua"]
            )

        if "server_salmuera" in self.datos_actual and "server_salmuera" in self.datos_anterior:
            estado_salmuera = self.evaluar_datos_salmuera(
                self.datos_actual["server_salmuera"], 
                self.datos_anterior["server_salmuera"]
            )
            
        # Actualizamos el historial para el próximo ciclo
        self.datos_anterior = self.datos_actual
        
        return estado_agua, estado_salmuera

    def _priorizar_estados(self, lista_estados):

        """Devuelve el estado más crítico de una lista de evaluaciones."""
        if "DETENER" in lista_estados:
            return "DETENER"
        elif "AJUSTAR" in lista_estados:
            return "AJUSTAR"
        else:
            return "NORMAL"

    
    def evaluar_datos_agua(self, datos_actual, datos_anterior):
        estados = {}
        
        if "tubo_h2_agua" in datos_actual:
            estados["tubo_h2_agua"] = self.evaluar_tubo_h2(datos_actual["tubo_h2_agua"], datos_anterior.get("tubo_h2_agua", {}))
            
        if "tubo_o2_agua" in datos_actual:
            estados["tubo_o2_agua"] = self.evaluar_tubo_o2(datos_actual["tubo_o2_agua"], datos_anterior.get("tubo_o2_agua", {}))

        if "deposito_h2_agua" in datos_actual:
            estados["deposito_h2_agua"] = self.evaluar_deposito_h2(datos_actual["deposito_h2_agua"], datos_anterior.get("deposito_h2_agua", {}))

        if "deposito_o2_agua" in datos_actual:
            estados["deposito_o2_agua"] = self.evaluar_deposito_o2(datos_actual["deposito_o2_agua"], datos_anterior.get("deposito_o2_agua", {}))

        return estados


    def evaluar_datos_salmuera(self, datos_actual, datos_anterior):
        estados = {}
        
        if "tubo_h2_salmuera" in datos_actual:
            estados["tubo_h2_salmuera"] = self.evaluar_tubo_h2(datos_actual["tubo_h2_salmuera"], datos_anterior.get("tubo_h2_salmuera", {}))

        if "tubo_cl2_salmuera" in datos_actual:
            estados["tubo_cl2_salmuera"] = self.evaluar_tubo_cl2(datos_actual["tubo_cl2_salmuera"], datos_anterior.get("tubo_cl2_salmuera", {}))

        if "deposito_h2_salmuera" in datos_actual:
            estados["deposito_h2_salmuera"] = self.evaluar_deposito_h2(datos_actual["deposito_h2_salmuera"], datos_anterior.get("deposito_h2_salmuera", {}))

        if "deposito_cl2_salmuera" in datos_actual:
            estados["deposito_cl2_salmuera"] = self.evaluar_deposito_cl2(datos_actual["deposito_cl2_salmuera"], datos_anterior.get("deposito_cl2_salmuera", {}))
        
        if "deposito_naoh_salmuera" in datos_actual:
            estados["deposito_naoh_salmuera"] = self.evaluar_deposito_naoh(datos_actual["deposito_naoh_salmuera"], datos_anterior.get("deposito_naoh_salmuera", {}))

        return estados

    
    def evaluar_tubo_h2(self, datos_actual, datos_anterior):

        print("--- Evaluando Tubo H2 ---")
        estados = []
        
        if "presion" in datos_actual and "presion" in datos_anterior:
            estados.append(self.evaluar_presion(datos_actual["presion"], datos_anterior["presion"]))
            
        if "concentracion" in datos_actual and "concentracion" in datos_anterior:
            estados.append(self.evaluar_concentracion(datos_actual["concentracion"], datos_anterior["concentracion"], "H2"))
            
        if "impurezas" in datos_actual and "impurezas" in datos_anterior:
            estados.append(self.evaluar_impurezas(datos_actual["impurezas"], datos_anterior["impurezas"], "Tubo H2"))

        return self._priorizar_estados(estados) if estados else "NORMAL"

    def evaluar_tubo_o2(self, datos_actual, datos_anterior):

        print("--- Evaluando Tubo O2 ---")
        estados = []
        
        if "presion" in datos_actual and "presion" in datos_anterior:
            estados.append(self.evaluar_presion(datos_actual["presion"], datos_anterior["presion"]))
            
        if "concentracion" in datos_actual and "concentracion" in datos_anterior:
            estados.append(self.evaluar_concentracion(datos_actual["concentracion"], datos_anterior["concentracion"], "O2"))
            
        if "impurezas" in datos_actual and "impurezas" in datos_anterior:
            estados.append(self.evaluar_impurezas(datos_actual["impurezas"], datos_anterior["impurezas"], "Tubo O2"))

        return self._priorizar_estados(estados) if estados else "NORMAL"

    def evaluar_tubo_cl2(self, datos_actual, datos_anterior):

        print("--- Evaluando Tubo Cl2 ---")
        estados = []
        
        if "presion" in datos_actual and "presion" in datos_anterior:
            estados.append(self.evaluar_presion(datos_actual["presion"], datos_anterior["presion"]))
            
        if "concentracion" in datos_actual and "concentracion" in datos_anterior:
            estados.append(self.evaluar_concentracion(datos_actual["concentracion"], datos_anterior["concentracion"], "Cl2"))
            
        if "impurezas" in datos_actual and "impurezas" in datos_anterior:
            estados.append(self.evaluar_impurezas(datos_actual["impurezas"], datos_anterior["impurezas"], "Tubo Cl2"))

        return self._priorizar_estados(estados) if estados else "NORMAL"

    
    def evaluar_deposito_h2(self, datos_actual, datos_anterior):

        print("--- Evaluando Depósito H2 ---")
        estados = []
        if "presion" in datos_actual and "presion" in datos_anterior:
            estados.append(self.evaluar_presion(datos_actual["presion"], datos_anterior["presion"]))
        if "cantidad" in datos_actual and "cantidad" in datos_anterior:
            estados.append(self.evaluar_cantidad(datos_actual["cantidad"], datos_anterior["cantidad"], "H2"))
        return self._priorizar_estados(estados) if estados else "NORMAL"

    def evaluar_deposito_o2(self, datos_actual, datos_anterior):

        print("--- Evaluando Depósito O2 ---")
        estados = []
        if "presion" in datos_actual and "presion" in datos_anterior:
            estados.append(self.evaluar_presion(datos_actual["presion"], datos_anterior["presion"]))
        if "cantidad" in datos_actual and "cantidad" in datos_anterior:
            estados.append(self.evaluar_cantidad(datos_actual["cantidad"], datos_anterior["cantidad"], "O2"))
        return self._priorizar_estados(estados) if estados else "NORMAL"

    def evaluar_deposito_cl2(self, datos_actual, datos_anterior):

        print("--- Evaluando Depósito Cl2 ---")
        estados = []
        if "presion" in datos_actual and "presion" in datos_anterior:
            estados.append(self.evaluar_presion(datos_actual["presion"], datos_anterior["presion"]))
        if "cantidad" in datos_actual and "cantidad" in datos_anterior:
            estados.append(self.evaluar_cantidad(datos_actual["cantidad"], datos_anterior["cantidad"], "Cl2"))
        return self._priorizar_estados(estados) if estados else "NORMAL"

    def evaluar_deposito_naoh(self, datos_actual, datos_anterior):

        print("--- Evaluando Depósito NaOH ---")
        estados = []
        if "cantidad" in datos_actual and "cantidad" in datos_anterior:
            estados.append(self.evaluar_cantidad(datos_actual["cantidad"], datos_anterior["cantidad"], "NaOH"))
        if "concentracion" in datos_actual and "concentracion" in datos_anterior:
            estados.append(self.evaluar_concentracion(datos_actual["concentracion"], datos_anterior["concentracion"], "NaOH"))
        return self._priorizar_estados(estados) if estados else "NORMAL"

    
    def evaluar_presion(self, presion_actual, presion_anterior):
        deltap = abs(presion_actual - presion_anterior)

        if presion_actual > 2.4:
            print("¡Alerta Crítica! La presión es demasiado alta.")
            return "DETENER"
        elif presion_actual < 1.8:
            print("Peligro de fuga. Presión por debajo del mínimo.")
            return "DETENER"
        elif deltap > 0.3:
            print("Cambio muy brusco de presión detectado.")
            return "DETENER" 
        elif presion_actual > 2.1:
            print("Advertencia: Presión acercándose al límite superior. Se requiere ajuste.")
            return "AJUSTAR"
        else:
            return "NORMAL"

    def evaluar_cantidad(self, cantidad_actual, cantidad_anterior, tipo_compuesto):
        delta_q = cantidad_actual - cantidad_anterior
            
        if delta_q < 0:
            print(f"¡Advertencia! Disminución de {tipo_compuesto} en el depósito. Posible fuga física o pérdida de datos.")
            return "AJUSTAR"
        elif delta_q > 50.0:  
            print(f"¡Anomalía Crítica! Aumento irreal en almacenamiento de {tipo_compuesto}. Posible ataque de inyección de datos.")
            return "DETENER"
        else:
            print(f"Almacenamiento de {tipo_compuesto} dentro de los parámetros de llenado normal.")
            return "NORMAL"

    def evaluar_concentracion(self, conc_actual, conc_anterior, tipo_compuesto):
        delta_c = abs(conc_actual - conc_anterior)
        
        if conc_actual < 0 or conc_actual > 100:
            print(f"¡Error de Sensor Crítico! La concentración de {tipo_compuesto} enviada está fuera del rango lógico (0-100%).")
            return "DETENER"
        elif delta_c > 10.0: 
            print(f"¡Alerta Crítica! Cambio extremadamente brusco en la concentración de {tipo_compuesto} detectado.")
            return "DETENER"
        elif delta_c > 5.0: 
            print(f"Advertencia: Fluctuación inusual en la concentración de {tipo_compuesto}. Se recomienda revisar el sensor.")
            return "AJUSTAR"
        else:
            print(f"Concentración de {tipo_compuesto} estable.")
            return "NORMAL"

    def evaluar_impurezas(self, impurezas_actual, impurezas_anterior, nombre_tubo):

        if impurezas_actual and not impurezas_anterior:
            print(f"¡ALERTA DE SEGURIDAD! Nuevas impurezas detectadas en el {nombre_tubo}. Riesgo de contaminación.")
            return "DETENER"
        elif impurezas_actual and impurezas_anterior:
            print(f"Advertencia: Las impurezas en el {nombre_tubo} persisten. Se requiere mantenimiento del sistema.")
            return "AJUSTAR"
        elif not impurezas_actual and impurezas_anterior:
            print(f"Nota: Las impurezas en el {nombre_tubo} han desaparecido bruscamente. Revisar posible infiltración de datos.")
            return "AJUSTAR"
        else:
            print(f"El {nombre_tubo} se mantiene libre de impurezas.")
            return "NORMAL"