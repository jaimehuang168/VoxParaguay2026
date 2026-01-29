/**
 * VoxParaguay 2026 - Localización Español Paraguayo (ES-PY)
 * Constantes de texto para la interfaz de usuario
 */

export const esPY = {
  // General
  app: {
    nombre: "VoxParaguay 2026",
    descripcion: "Sistema de Encuestas y Análisis de Opinión Pública",
    version: "1.0.0",
  },

  // Navegación
  nav: {
    inicio: "Inicio",
    panel: "Panel de Control",
    campanas: "Campañas",
    encuestas: "Encuestas",
    agentes: "Agentes",
    analisis: "Análisis",
    mapa: "Mapa",
    configuracion: "Configuración",
    cerrarSesion: "Cerrar Sesión",
  },

  // Dashboard
  dashboard: {
    titulo: "Panel de Control",
    bienvenida: "Bienvenido/a",
    encuestasHoy: "Encuestas Hoy",
    respuestasTotales: "Respuestas Totales",
    tasaRespuesta: "Tasa de Respuesta",
    agentesActivos: "Agentes Activos",
    conversacionesActivas: "Conversaciones Activas",
    tiempoPromedio: "Tiempo Promedio",
  },

  // Agentes
  agentes: {
    titulo: "Gestión de Agentes",
    estado: {
      disponible: "Disponible",
      ocupado: "Ocupado",
      descanso: "En Descanso",
      desconectado: "Desconectado",
    },
    acciones: {
      conectar: "Conectar",
      desconectar: "Desconectar",
      tomarDescanso: "Tomar Descanso",
      volverDisponible: "Volver Disponible",
    },
    metricas: {
      encuestasCompletadas: "Encuestas Completadas",
      tiempoPromedio: "Tiempo Promedio por Encuesta",
      calificacion: "Calificación",
      cargaActual: "Carga Actual",
    },
  },

  // Canales
  canales: {
    voz: "Llamada de Voz",
    whatsapp: "WhatsApp",
    facebook: "Facebook Messenger",
    instagram: "Instagram Direct",
    sms: "Mensaje SMS",
  },

  // Encuestas
  encuestas: {
    titulo: "Encuestas",
    pregunta: "Pregunta",
    respuesta: "Respuesta",
    completada: "Completada",
    enProgreso: "En Progreso",
    cancelada: "Cancelada",
    tipoRespuesta: {
      texto: "Texto Libre",
      opcionMultiple: "Opción Múltiple",
      escala: "Escala (1-5)",
      siNo: "Sí/No",
      calificacion: "Calificación con Emojis",
    },
    emojis: {
      muyMalo: "Muy Malo",
      malo: "Malo",
      neutral: "Neutral",
      bueno: "Bueno",
      muyBueno: "Muy Bueno",
    },
  },

  // Análisis
  analisis: {
    titulo: "Análisis de Datos",
    sentimiento: {
      titulo: "Análisis de Sentimiento",
      positivo: "Positivo",
      negativo: "Negativo",
      neutral: "Neutral",
      muyPositivo: "Muy Positivo",
      muyNegativo: "Muy Negativo",
    },
    metricas: {
      totalEncuestas: "Total de Encuestas",
      tasaCompletacion: "Tasa de Completación",
      sentimientoPromedio: "Sentimiento Promedio",
      temasIdentificados: "Temas Identificados",
    },
    graficos: {
      tendenciaSemanal: "Tendencia Semanal",
      distribucionRegional: "Distribución Regional",
      temasPrincipales: "Temas Principales",
      comparacionCanales: "Comparación por Canal",
    },
  },

  // Mapa
  mapa: {
    titulo: "Mapa de Opinión Pública",
    leyenda: {
      titulo: "Índice de Sentimiento",
      muyPositivo: "Muy positivo (+30%)",
      positivo: "Positivo (+10%)",
      neutral: "Neutral",
      negativo: "Negativo (-10%)",
      muyNegativo: "Muy negativo (-30%)",
    },
    panel: {
      titulo: "Análisis Detallado",
      encuestas: "Encuestas",
      sentimiento: "Sentimiento",
      temasPrincipales: "Temas Principales",
      detallePorTema: "Detalle por Tema",
      resumenIA: "Resumen de Inteligencia Artificial",
      generandoAnalisis: "Generando análisis...",
    },
    tooltip: {
      capital: "Capital",
      poblacion: "Población",
      sentimiento: "Sentimiento",
    },
  },

  // Departamentos de Paraguay
  departamentos: {
    asuncion: "Asunción",
    central: "Central",
    alto_parana: "Alto Paraná",
    itapua: "Itapúa",
    san_pedro: "San Pedro",
    caaguazu: "Caaguazú",
    paraguari: "Paraguarí",
    guaira: "Guairá",
    caazapa: "Caazapá",
    misiones: "Misiones",
    neembucu: "Ñeembucú",
    amambay: "Amambay",
    canindeyu: "Canindeyú",
    presidente_hayes: "Presidente Hayes",
    boqueron: "Boquerón",
    alto_paraguay: "Alto Paraguay",
    concepcion: "Concepción",
    cordillera: "Cordillera",
  },

  // Regiones
  regiones: {
    oriental: "Región Oriental",
    occidental: "Región Occidental (Chaco)",
  },

  // Tiempo
  tiempo: {
    hoy: "Hoy",
    ayer: "Ayer",
    estaSemana: "Esta Semana",
    esteMes: "Este Mes",
    esteAno: "Este Año",
    personalizado: "Personalizado",
    hace: "Hace",
    minutos: "minutos",
    horas: "horas",
    dias: "días",
    semanas: "semanas",
  },

  // Acciones
  acciones: {
    guardar: "Guardar",
    cancelar: "Cancelar",
    eliminar: "Eliminar",
    editar: "Editar",
    crear: "Crear",
    buscar: "Buscar",
    filtrar: "Filtrar",
    exportar: "Exportar",
    importar: "Importar",
    actualizar: "Actualizar",
    confirmar: "Confirmar",
    enviar: "Enviar",
    cerrar: "Cerrar",
    verMas: "Ver Más",
    verMenos: "Ver Menos",
    seleccionar: "Seleccionar",
    descargar: "Descargar",
  },

  // Mensajes
  mensajes: {
    exito: "Operación exitosa",
    error: "Ha ocurrido un error",
    cargando: "Cargando...",
    sinDatos: "No hay datos disponibles",
    sinResultados: "No se encontraron resultados",
    confirmarEliminar: "¿Está seguro que desea eliminar este elemento?",
    cambiosGuardados: "Los cambios han sido guardados",
    sesionExpirada: "Su sesión ha expirado",
    conexionPerdida: "Se perdió la conexión",
    reconectando: "Reconectando...",
    sinConexion: "Sin conexión a Internet",
    offline: "Modo sin conexión",
  },

  // Fechas
  fechas: {
    dias: ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"],
    diasCortos: ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"],
    meses: [
      "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
      "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ],
    mesesCortos: [
      "Ene", "Feb", "Mar", "Abr", "May", "Jun",
      "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
    ],
  },

  // Formatos
  formatos: {
    fecha: "dd/MM/yyyy",
    fechaHora: "dd/MM/yyyy HH:mm",
    hora: "HH:mm",
    moneda: "₲",
    decimal: ",",
    miles: ".",
  },

  // Validaciones
  validaciones: {
    requerido: "Este campo es requerido",
    emailInvalido: "Correo electrónico inválido",
    telefonoInvalido: "Número de teléfono inválido",
    minimoCaracteres: "Mínimo {min} caracteres",
    maximoCaracteres: "Máximo {max} caracteres",
    soloNumeros: "Solo se permiten números",
    cedulaInvalida: "Número de cédula inválido",
  },

  // Expresiones paraguayas (para uso en análisis de Jopara)
  jopara: {
    expresiones: {
      "nde": "vos/tu",
      "che": "yo/mi",
      "ndaikuaai": "no sé",
      "haiku": "no hay",
      "oime": "hay/existe",
      "ipora": "está bien/es bueno",
      "ndaiporai": "no está bien",
      "ko'ape": "aquí",
      "upape": "allá",
    },
    nota: "Sistema de detección de Jopara (español-guaraní) activo",
  },
} as const;

// Tipo para autocompletado
export type LocaleKey = typeof esPY;

// Función helper para formatear números
export function formatNumber(num: number): string {
  return num.toLocaleString("es-PY");
}

// Función helper para formatear fechas
export function formatDate(date: Date, format: "fecha" | "fechaHora" | "hora" = "fecha"): string {
  const options: Intl.DateTimeFormatOptions =
    format === "fecha"
      ? { day: "2-digit", month: "2-digit", year: "numeric" }
      : format === "fechaHora"
        ? { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" }
        : { hour: "2-digit", minute: "2-digit" };

  return date.toLocaleDateString("es-PY", options);
}

// Función helper para formatear moneda (Guaraníes)
export function formatCurrency(amount: number): string {
  return `₲ ${formatNumber(amount)}`;
}
