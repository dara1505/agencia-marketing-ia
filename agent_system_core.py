"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    SISTEMA DE AGENTES IA - ARQUITECTURA                  ║
║                                                                           ║
║  ORQUESTADOR PRINCIPAL + 6 AGENTES ESPECIALIZADOS                        ║
║                                                                           ║
║  Agentes:                                                                 ║
║  1. Strategy Agent - Analiza briefing, propone estrategia                ║
║  2. Content Agent - Genera contenido (posts, artículos)                  ║
║  3. Design Agent - Crea prompts de imagen profesionales                  ║
║  4. Video Agent - Genera guiones de video cinematográficos               ║
║  5. Ads Agent - Crea campañas Google/Meta optimizadas                    ║
║  6. Automation Agent - Diseña workflows inteligentes                     ║
║                                                                           ║
║  El sistema APRENDE del cliente a medida que lo conoce mejor             ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import json
import asyncio
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

# ==================== TIPOS Y MODELOS ====================

class AgentRole(Enum):
    ORCHESTRATOR = "orchestrator"
    STRATEGY = "strategy"
    CONTENT = "content"
    DESIGN = "design"
    VIDEO = "video"
    ADS = "ads"
    AUTOMATION = "automation"

@dataclass
class ClientProfile:
    """Perfil del cliente - Evoluciona con el tiempo"""
    id: str
    nombre: str
    tipo_negocio: str
    objetivo: str
    publico_objetivo: str
    presupuesto: float
    descripcion: str
    created_at: str
    
    # Aprendizaje del cliente
    historial_campanas: List[Dict] = None
    preferencias_contenido: Dict = None
    tono_voz: str = None
    valores_marca: List[str] = None
    competidores: List[str] = None
    
    def __post_init__(self):
        if self.historial_campanas is None:
            self.historial_campanas = []
        if self.preferencias_contenido is None:
            self.preferencias_contenido = {}
        if self.valores_marca is None:
            self.valores_marca = []

@dataclass
class CampaignBrief:
    """Brief de campaña proporcionado por cliente"""
    client_id: str
    nombre_campaña: str
    objetivo_especifico: str
    canal_principal: str
    duracion_semanas: int
    presupuesto: float
    target_metrics: Dict
    additional_context: str = ""

@dataclass
class AgentResponse:
    """Respuesta estandarizada de un agente"""
    agent: AgentRole
    timestamp: str
    data: Dict
    reasoning: str
    confidence: float  # 0-1, qué tan seguro está el agente

@dataclass
class CampaignOutput:
    """Output final de campaña completa"""
    campaign_id: str
    client_id: str
    timestamp: str
    
    # Outputs de cada agente
    strategy: AgentResponse
    content: AgentResponse
    design: AgentResponse
    video: AgentResponse
    ads: AgentResponse
    automation: AgentResponse
    
    # Meta
    status: str = "draft"  # draft, approved, active
    feedback: Dict = None

# ==================== BASE DE DATOS DE CONOCIMIENTO ====================

INDUSTRY_KNOWLEDGE = {
    "Salud": {
        "key_themes": ["Educación", "Confianza", "Resultados verificables"],
        "content_pillars": [
            "Educación en salud",
            "Prevención",
            "Testimonios reales",
            "Expertise"
        ],
        "visual_style": "Profesional, limpio, confiable",
        "tone": "Educativo pero accesible",
        "compliance": ["Disclaimers médicos", "No prometer curas"],
        "platforms": ["Instagram", "LinkedIn", "Blog", "Email"],
        "common_ctas": [
            "Agendar consulta",
            "Descargar guía",
            "Ver testimonios"
        ]
    },
    "E-commerce": {
        "key_themes": ["Urgencia", "Social proof", "Beneficios"],
        "content_pillars": [
            "Product showcase",
            "User reviews",
            "Guías de compra",
            "Flash sales"
        ],
        "visual_style": "Vibrante, atractivo, moderno",
        "tone": "Conversacional, urgente",
        "compliance": [],
        "platforms": ["Instagram", "TikTok", "Facebook", "Pinterest"],
        "common_ctas": [
            "Comprar ahora",
            "Ver colección",
            "Oferta limitada"
        ]
    },
    "SaaS": {
        "key_themes": ["Eficiencia", "ROI", "Escalabilidad"],
        "content_pillars": [
            "Product demos",
            "Case studies",
            "ROI calculators",
            "Comparativas"
        ],
        "visual_style": "Moderno, técnico, profesional",
        "tone": "Dato-driven, claro",
        "compliance": [],
        "platforms": ["LinkedIn", "Twitter", "Blog", "Email"],
        "common_ctas": [
            "Iniciar trial",
            "Ver demo",
            "Hablar con ventas"
        ]
    },
    "Servicios": {
        "key_themes": ["Expertise", "Resultados", "Confiabilidad"],
        "content_pillars": [
            "Casos de éxito",
            "Proceso",
            "Testimonios",
            "Expertise showcase"
        ],
        "visual_style": "Profesional, sofisticado",
        "tone": "Confiable, experto",
        "compliance": [],
        "platforms": ["LinkedIn", "Instagram", "Blog", "Email"],
        "common_ctas": [
            "Solicitar propuesta",
            "Agendar consulta",
            "Descargar caso de estudio"
        ]
    }
}

# ==================== AGENTES ESPECIALIZADOS ====================

class Agent:
    """Base class para todos los agentes"""
    
    def __init__(self, role: AgentRole, client: ClientProfile):
        self.role = role
        self.client = client
        self.industry_data = INDUSTRY_KNOWLEDGE.get(client.tipo_negocio, {})
        self.memory = []  # Para aprendizaje iterativo
    
    async def think(self, brief: CampaignBrief, context: Dict) -> AgentResponse:
        """Método que implementan agentes especializados"""
        raise NotImplementedError
    
    def _learn_from_feedback(self, feedback: Dict):
        """Aprende de feedback para mejorar futuras respuestas"""
        self.memory.append({
            'timestamp': datetime.now().isoformat(),
            'feedback': feedback
        })

class StrategyAgent(Agent):
    """Analiza briefing y propone estrategia integral"""
    
    async def think(self, brief: CampaignBrief, context: Dict) -> AgentResponse:
        # Análisis del briefing
        cpa_base = brief.presupuesto / 10
        
        if brief.presupuesto <= 100:
            approach = "LEAN: 70% orgánico, 30% pagado"
            phases = {
                "fase_1": "Construcción presencia",
                "fase_2": "Escalado mínimo pagado",
                "fase_3": "Optimización"
            }
        elif brief.presupuesto <= 500:
            approach = "GROWTH: 50/50 orgánico/pagado"
            phases = {
                "fase_1": "Setup completo",
                "fase_2": "Escalado activo",
                "fase_3": "Dominio de canal"
            }
        else:
            approach = "FULL SERVICE: Máximo ROI"
            phases = {
                "fase_1": "Lanzamiento simultáneo",
                "fase_2": "Escalado agresivo",
                "fase_3": "Dominio de mercado"
            }
        
        strategy = {
            "approach": approach,
            "budget_allocation": {
                "google_ads": brief.presupuesto * 0.35,
                "social_paid": brief.presupuesto * 0.30,
                "content": brief.presupuesto * 0.15,
                "automation": brief.presupuesto * 0.10,
                "contingency": brief.presupuesto * 0.10
            },
            "phases": phases,
            "kpis": {
                "leads_meta": int(brief.presupuesto / cpa_base),
                "cpa_objetivo": cpa_base,
                "conversion_target": 0.035,
                "roi_esperado": "2.5:1 a 3.5:1"
            },
            "key_insight": f"Para {self.client.publico_objetivo}, enfoque en {self.industry_data.get('key_themes', ['engagement'])[0]}"
        }
        
        return AgentResponse(
            agent=AgentRole.STRATEGY,
            timestamp=datetime.now().isoformat(),
            data=strategy,
            reasoning="Análisis de presupuesto, industria y objetivo. Estrategia adaptada a escala.",
            confidence=0.95
        )

class ContentAgent(Agent):
    """Genera contenido: posts, artículos, copy"""
    
    async def think(self, brief: CampaignBrief, context: Dict) -> AgentResponse:
        pillars = self.industry_data.get('content_pillars', [])
        ctas = self.industry_data.get('common_ctas', [])
        tone = self.industry_data.get('tone', 'Profesional')
        
        posts = []
        for i, pillar in enumerate(pillars[:4]):
            posts.append({
                "id": i + 1,
                "tipo": pillar,
                "copy_template": f"[Hook relacionado a {pillar}] → [Valor/Educación] → [{ctas[i % len(ctas)]}]",
                "tone": tone,
                "platforms": self.industry_data.get('platforms', [])
            })
        
        articulos = [
            {
                "titulo": f"Guía completa: {pillars[0]} en {datetime.now().year}",
                "palabras_clave": ["placeholder"],
                "estructura": ["Intro", "Puntos principales", "Conclusión", "CTA"],
                "longitud": "1500-2000 palabras"
            },
            {
                "titulo": f"Cómo maximizar tu {brief.objetivo_especifico}",
                "palabras_clave": ["placeholder"],
                "estructura": ["Intro", "3 estrategias principales", "Caso de éxito", "CTA"],
                "longitud": "1200-1500 palabras"
            }
        ]
        
        content_output = {
            "posts": posts,
            "articulos": articulos,
            "email_sequences": self._generate_email_sequences(ctas),
            "storytelling_angles": [
                f"El origen de {self.client.nombre}",
                f"Por qué {brief.objetivo_especifico} importa",
                f"Transformación de cliente: caso de éxito"
            ]
        }
        
        return AgentResponse(
            agent=AgentRole.CONTENT,
            timestamp=datetime.now().isoformat(),
            data=content_output,
            reasoning=f"Contenido basado en pillars de {self.client.tipo_negocio}. Tono: {tone}",
            confidence=0.88
        )
    
    def _generate_email_sequences(self, ctas: List[str]) -> List[Dict]:
        return [
            {
                "nombre": "Welcome Series",
                "emails": [
                    {"dia": 0, "subject": "Bienvenida", "objetivo": "Presentación"},
                    {"dia": 2, "subject": "Valor principal", "objetivo": "Educación"},
                    {"dia": 5, "subject": "Testimonios", "objetivo": "Social proof"}
                ]
            }
        ]

class DesignAgent(Agent):
    """Crea prompts de imagen profesionales para IA"""
    
    async def think(self, brief: CampaignBrief, context: Dict) -> AgentResponse:
        visual_style = self.industry_data.get('visual_style', 'Profesional')
        
        prompts = [
            {
                "id": 1,
                "tipo": "Hero Image",
                "prompt": self._craft_prompt(
                    f"{visual_style} image for {brief.objective_especifico}",
                    [self.client.publico_objetivo, "professional", "high quality"],
                    "1:1"
                ),
                "aspecto": "1:1",
                "uso": "Instagram/Facebook"
            },
            {
                "id": 2,
                "tipo": "Social Proof",
                "prompt": self._craft_prompt(
                    f"Happy customer using {self.client.nombre} service",
                    [self.client.publico_objetivo, "testimonial", "authentic"],
                    "16:9"
                ),
                "aspecto": "16:9",
                "uso": "Instagram Stories"
            },
            {
                "id": 3,
                "tipo": "Educational",
                "prompt": self._craft_prompt(
                    f"Infographic about {brief.objetivo_especifico}",
                    ["educational", "clear", "data-driven"],
                    "16:9"
                ),
                "aspecto": "16:9",
                "uso": "Blog/LinkedIn"
            }
        ]
        
        design_output = {
            "prompts": prompts,
            "brand_guidelines": {
                "style": visual_style,
                "aesthetic": self.industry_data.get('visual_style', ''),
                "recommended_tools": ["Midjourney", "DALL-E 3", "Photoshop"]
            },
            "image_calendar": self._create_image_calendar()
        }
        
        return AgentResponse(
            agent=AgentRole.DESIGN,
            timestamp=datetime.now().isoformat(),
            data=design_output,
            reasoning=f"Prompts diseñados para {visual_style}. Listos para IA generativa.",
            confidence=0.90
        )
    
    def _craft_prompt(self, main: str, modifiers: List[str], aspect: str) -> str:
        return f"{main}. Style: {self.industry_data.get('visual_style', '')}. Details: {', '.join(modifiers)}. Aspect ratio: {aspect}. Professional photography. High quality."
    
    def _create_image_calendar(self) -> List[Dict]:
        return [
            {"semana": 1, "cantidad": 3, "temas": ["Hero", "Benefit 1", "Benefit 2"]},
            {"semana": 2, "cantidad": 3, "temas": ["Testimonial", "Process", "Result"]},
            {"semana": 3, "cantidad": 3, "temas": ["Educational", "Case study", "CTA"]}
        ]

class VideoAgent(Agent):
    """Genera guiones de video cinematográficos"""
    
    async def think(self, brief: CampaignBrief, context: Dict) -> AgentResponse:
        tone = self.industry_data.get('tone', 'Profesional')
        ctas = self.industry_data.get('common_ctas', [])
        
        videos = [
            {
                "id": 1,
                "titulo": "Hook + Value (30 seg)",
                "estructura": [
                    "0-3s: HOOK explosivo",
                    "3-20s: Valor principal (2 puntos)",
                    "20-27s: Proof/Testimonial",
                    "27-30s: CTA"
                ],
                "cta": ctas[0],
                "platform": "TikTok/Reels",
                "tone": tone
            },
            {
                "id": 2,
                "titulo": "Educational (60 seg)",
                "estructura": [
                    "0-5s: Pregunta provocadora",
                    "5-45s: Respuesta educativa (máx 3 puntos)",
                    "45-55s: Story/Ejemplo",
                    "55-60s: CTA soft"
                ],
                "cta": ctas[1] if len(ctas) > 1 else ctas[0],
                "platform": "YouTube",
                "tone": tone
            },
            {
                "id": 3,
                "titulo": "Transformation (15-30 seg)",
                "estructura": [
                    "0-2s: Problema (before)",
                    "2-8s: Solución",
                    "8-13s: Resultado (after)",
                    "13-15s: CTA"
                ],
                "cta": ctas[2] if len(ctas) > 2 else ctas[0],
                "platform": "Instagram/TikTok",
                "tone": tone
            }
        ]
        
        video_output = {
            "video_templates": videos,
            "production_tips": [
                "Grabar en vertical para móvil",
                "Audio clear y energético",
                "Subtítulos obligatorios",
                "Editar con CapCut (gratuito)"
            ],
            "publishing_strategy": {
                "frecuencia": "3-5 videos por semana",
                "mejor_hora": "9am, 1pm, 7pm",
                "repurposing": "1 video → 5 formatos diferentes"
            }
        }
        
        return AgentResponse(
            agent=AgentRole.VIDEO,
            timestamp=datetime.now().isoformat(),
            data=video_output,
            reasoning=f"Guiones diseñados para máximo engagement. Optimizados para scroll/mobile.",
            confidence=0.87
        )

class AdsAgent(Agent):
    """Crea campañas Google/Meta optimizadas"""
    
    async def think(self, brief: CampaignBrief, context: Dict) -> AgentResponse:
        presupuesto_google = brief.presupuesto * 0.40
        presupuesto_meta = brief.presupuesto * 0.35
        
        ads = {
            "google_ads": {
                "presupuesto_mensual": presupuesto_google,
                "tipo_campana": "Search + Display",
                "palabras_clave": self._generate_keywords(brief),
                "ad_copy_templates": [
                    {
                        "headline": f"[Benefit] para {self.client.publico_objetivo}",
                        "description": f"{brief.objetivo_especifico} profesional. Resultados verificables.",
                        "cta": "Saber más"
                    }
                ],
                "landing_page": "Optimizada para conversión",
                "cpa_objetivo": brief.presupuesto / 10
            },
            "meta_ads": {
                "presupuesto_mensual": presupuesto_meta,
                "tipos_anuncios": ["Carousel", "Video", "Collection"],
                "audience": {
                    "target": self.client.publico_objetivo,
                    "lookalike": True,
                    "retargeting": True
                },
                "creative_strategy": [
                    {"tipo": "User-generated content", "performance": "Alto"},
                    {"tipo": "Testimonials", "performance": "Alto"},
                    {"tipo": "Problem-agitate-solve", "performance": "Medio"}
                ],
                "testing": "3 variantes A/B semanales"
            },
            "attribution": {
                "pixel_setup": "Meta Pixel + Google Analytics 4",
                "tracking": "UTM + conversion tracking",
                "reporting": "Dashboard automático diario"
            }
        }
        
        return AgentResponse(
            agent=AgentRole.ADS,
            timestamp=datetime.now().isoformat(),
            data=ads,
            reasoning=f"Presupuesto distribuido: Google ${presupuesto_google}, Meta ${presupuesto_meta}",
            confidence=0.92
        )
    
    def _generate_keywords(self, brief: CampaignBrief) -> List[str]:
        return [
            brief.objetivo_especifico,
            f"{brief.objetivo_especifico} para {self.client.publico_objetivo}",
            f"Mejor {brief.objetivo_especifico}",
            f"Cómo {brief.objetivo_especifico}"
        ]

class AutomationAgent(Agent):
    """Diseña workflows automáticos"""
    
    async def think(self, brief: CampaignBrief, context: Dict) -> AgentResponse:
        automations = {
            "email_workflows": [
                {
                    "nombre": "Lead Nurture Series",
                    "trigger": "Lead captured",
                    "emails": [
                        {"dia": 0, "type": "Welcome"},
                        {"dia": 2, "type": "Educativo"},
                        {"dia": 5, "type": "Social proof"},
                        {"dia": 7, "type": "CTA final"}
                    ]
                },
                {
                    "nombre": "Re-engagement",
                    "trigger": "No open 14 días",
                    "action": "Enviar offer especial"
                }
            ],
            "sms_automation": {
                "lead_nurture": "SMS 48h post-lead",
                "cita_recordatorio": "24h antes de cita",
                "follow_up": "Post-compra"
            },
            "social_automation": {
                "publication": "Programación automática",
                "engagement": "Auto-responder comentarios",
                "monitoring": "Escucha de menciones"
            },
            "n8n_workflows": [
                {
                    "nombre": "Lead to CRM",
                    "steps": ["Capturar lead", "Validar email", "Crear en CRM", "Enviar welcome email"],
                    "trigger": "Form submission"
                },
                {
                    "nombre": "Sync Social to Email",
                    "steps": ["Monitorear menciones", "Crear contact", "Agregar a list"],
                    "trigger": "New mention"
                }
            ]
        }
        
        return AgentResponse(
            agent=AgentRole.AUTOMATION,
            timestamp=datetime.now().isoformat(),
            data=automations,
            reasoning="Workflows diseñados para máxima eficiencia. n8n-ready.",
            confidence=0.89
        )

# ==================== ORQUESTADOR PRINCIPAL ====================

class CampaignOrchestrator:
    """Orquesta todos los agentes"""
    
    def __init__(self, client: ClientProfile):
        self.client = client
        self.strategy_agent = StrategyAgent(AgentRole.STRATEGY, client)
        self.content_agent = ContentAgent(AgentRole.CONTENT, client)
        self.design_agent = DesignAgent(AgentRole.DESIGN, client)
        self.video_agent = VideoAgent(AgentRole.VIDEO, client)
        self.ads_agent = AdsAgent(AgentRole.ADS, client)
        self.automation_agent = AutomationAgent(AgentRole.AUTOMATION, client)
        
        self.agents = [
            self.strategy_agent,
            self.content_agent,
            self.design_agent,
            self.video_agent,
            self.ads_agent,
            self.automation_agent
        ]
    
    async def generate_campaign(self, brief: CampaignBrief) -> CampaignOutput:
        """Genera campaña completa coordinando todos los agentes"""
        
        print(f"\n🚀 Generando campaña para {self.client.nombre}...")
        
        # Contexto compartido entre agentes
        context = {
            'client': self.client,
            'brief': brief
        }
        
        # Ejecutar agentes en paralelo
        tasks = [
            self.strategy_agent.think(brief, context),
            self.content_agent.think(brief, context),
            self.design_agent.think(brief, context),
            self.video_agent.think(brief, context),
            self.ads_agent.think(brief, context),
            self.automation_agent.think(brief, context)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # Construir output final
        campaign = CampaignOutput(
            campaign_id=f"camp_{datetime.now().timestamp()}",
            client_id=self.client.id,
            timestamp=datetime.now().isoformat(),
            strategy=responses[0],
            content=responses[1],
            design=responses[2],
            video=responses[3],
            ads=responses[4],
            automation=responses[5]
        )
        
        print("✅ Campaña generada exitosamente!")
        return campaign
    
    def output_as_dict(self, campaign: CampaignOutput) -> Dict:
        """Convierte a diccionario para serializar"""
        return {
            'campaign_id': campaign.campaign_id,
            'client_id': campaign.client_id,
            'timestamp': campaign.timestamp,
            'strategy': {
                'agent': campaign.strategy.agent.value,
                'data': campaign.strategy.data,
                'reasoning': campaign.strategy.reasoning,
                'confidence': campaign.strategy.confidence
            },
            'content': {
                'agent': campaign.content.agent.value,
                'data': campaign.content.data,
                'reasoning': campaign.content.reasoning,
                'confidence': campaign.content.confidence
            },
            'design': {
                'agent': campaign.design.agent.value,
                'data': campaign.design.data,
                'reasoning': campaign.design.reasoning,
                'confidence': campaign.design.confidence
            },
            'video': {
                'agent': campaign.video.agent.value,
                'data': campaign.video.data,
                'reasoning': campaign.video.reasoning,
                'confidence': campaign.video.confidence
            },
            'ads': {
                'agent': campaign.ads.agent.value,
                'data': campaign.ads.data,
                'reasoning': campaign.ads.reasoning,
                'confidence': campaign.ads.confidence
            },
            'automation': {
                'agent': campaign.automation.agent.value,
                'data': campaign.automation.data,
                'reasoning': campaign.automation.reasoning,
                'confidence': campaign.automation.confidence
            }
        }

# ==================== MAIN - TESTING ====================

async def main():
    """Ejemplo de uso del sistema"""
    
    # Crear cliente
    client = ClientProfile(
        id="client_001",
        nombre="Dra. Mirle Noroño",
        tipo_negocio="Salud",
        objetivo="Generar Leads",
        publico_objetivo="Mujeres 25-45 interesadas en nutrición",
        presupuesto=500,
        descripcion="Nutrióloga especializada en nutrición personalizada",
        created_at=datetime.now().isoformat()
    )
    
    # Crear brief
    brief = CampaignBrief(
        client_id=client.id,
        nombre_campaña="Atracción de pacientes Q1 2024",
        objetivo_especifico="Aumentar citas de nutrición",
        canal_principal="Instagram + Google",
        duracion_semanas=12,
        presupuesto=500,
        target_metrics={"leads": 50, "conversión": 0.15},
        additional_context="Nuevo servicio de nutrición online"
    )
    
    # Crear orquestador y generar campaña
    orchestrator = CampaignOrchestrator(client)
    campaign = await orchestrator.generate_campaign(brief)
    
    # Mostrar resultados
    output = orchestrator.output_as_dict(campaign)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    
    # Guardar a archivo
    with open('campaign_output.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Campaña guardada en campaign_output.json")

if __name__ == "__main__":
    asyncio.run(main())
