"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                     BACKEND FASTAPI - AGENCIA IA                         ║
║                                                                           ║
║  API REST para administración de campañas, clientes, agentes              ║
║  Conecta: Supabase + Agentes Python + Integraciones externas             ║
║                                                                           ║
║  Uso: uvicorn app:app --reload                                          ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import asyncio
import json
from datetime import datetime
from enum import Enum
import os
from dotenv import load_dotenv

# Imports locales
import sys
sys.path.append('.')
from agent_system_core import (
    ClientProfile, CampaignBrief, CampaignOrchestrator,
    INDUSTRY_KNOWLEDGE
)

load_dotenv()

# ==================== CONFIGURACIÓN ====================

app = FastAPI(
    title="Agencia Marketing IA API",
    description="Sistema de gestión de campañas con agentes IA",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELOS PYDANTIC ====================

class CreateClientRequest(BaseModel):
    nombre: str
    email: EmailStr
    tipo_negocio: str
    objetivo: str
    publico_objetivo: str
    presupuesto: float
    descripcion: str

class UpdateClientRequest(BaseModel):
    nombre: Optional[str] = None
    objetivo: Optional[str] = None
    publico_objetivo: Optional[str] = None
    presupuesto: Optional[float] = None
    descripcion: Optional[str] = None
    tono_voz: Optional[str] = None
    valores_marca: Optional[List[str]] = None

class CreateCampaignRequest(BaseModel):
    client_id: str
    nombre_campaña: str
    objetivo_especifico: str
    canal_principal: str
    duracion_semanas: int
    presupuesto: float
    additional_context: Optional[str] = None

class ClientFeedbackRequest(BaseModel):
    campaign_id: str
    agent_type: str
    rating: int  # 1-5
    comentario: str
    mejoras_sugeridas: Optional[List[str]] = None

class IntegrationRequest(BaseModel):
    platform: str  # meta, google, email, n8n
    access_token: Optional[str] = None
    configuracion: Dict[str, Any] = {}

class ActivateWorkflowRequest(BaseModel):
    campaign_id: str
    workflow_type: str  # email_campaign, facebook_ads, google_ads, n8n_workflow

# ==================== RESPUESTAS ====================

class ClientResponse(BaseModel):
    id: str
    nombre: str
    email: str
    tipo_negocio: str
    objetivo: str
    publico_objetivo: str
    presupuesto: float
    created_at: str
    campanas_activas: int = 0

class CampaignResponse(BaseModel):
    id: str
    client_id: str
    nombre: str
    objetivo_especifico: str
    estado: str
    presupuesto: float
    created_at: str
    output_agentes: Optional[Dict] = None

class MetricsResponse(BaseModel):
    campaign_id: str
    leads_generados: int
    conversiones: int
    cpa_actual: float
    roi_actual: float
    fecha: str

# ==================== STORAGE MOCK (Será Supabase en producción) ====================

class InMemoryDB:
    """Storage en memoria para desarrollo. En producción usar Supabase."""
    
    def __init__(self):
        self.clients: Dict[str, Dict] = {}
        self.campaigns: Dict[str, Dict] = {}
        self.integrations: Dict[str, Dict] = {}
        self.metrics: Dict[str, List[Dict]] = {}
        self.activations: List[Dict] = []
    
    # CLIENTES
    async def create_client(self, data: CreateClientRequest) -> Dict:
        client_id = f"client_{datetime.now().timestamp()}"
        client = {
            'id': client_id,
            'nombre': data.nombre,
            'email': data.email,
            'tipo_negocio': data.tipo_negocio,
            'objetivo': data.objetivo,
            'publico_objetivo': data.publico_objetivo,
            'presupuesto': data.presupuesto,
            'descripcion': data.descripcion,
            'created_at': datetime.now().isoformat(),
            'campanas': []
        }
        self.clients[client_id] = client
        return client
    
    async def get_client(self, client_id: str) -> Optional[Dict]:
        return self.clients.get(client_id)
    
    async def list_clients(self) -> List[Dict]:
        return list(self.clients.values())
    
    async def update_client(self, client_id: str, data: UpdateClientRequest) -> Dict:
        if client_id not in self.clients:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        client = self.clients[client_id]
        update_data = data.dict(exclude_unset=True)
        client.update(update_data)
        client['updated_at'] = datetime.now().isoformat()
        return client
    
    # CAMPAÑAS
    async def create_campaign(self, data: CreateCampaignRequest, output: Dict) -> Dict:
        campaign_id = f"camp_{datetime.now().timestamp()}"
        campaign = {
            'id': campaign_id,
            'client_id': data.client_id,
            'nombre': data.nombre_campaña,
            'objetivo_especifico': data.objetivo_especifico,
            'canal_principal': data.canal_principal,
            'duracion_semanas': data.duracion_semanas,
            'presupuesto': data.presupuesto,
            'estado': 'draft',
            'output_agentes': output,
            'created_at': datetime.now().isoformat(),
            'feedback': []
        }
        self.campaigns[campaign_id] = campaign
        
        # Agregar a cliente
        if data.client_id in self.clients:
            self.clients[data.client_id]['campanas'].append(campaign_id)
        
        return campaign
    
    async def get_campaign(self, campaign_id: str) -> Optional[Dict]:
        return self.campaigns.get(campaign_id)
    
    async def list_campaigns(self, client_id: str) -> List[Dict]:
        return [c for c in self.campaigns.values() if c['client_id'] == client_id]
    
    async def update_campaign_status(self, campaign_id: str, status: str) -> Dict:
        if campaign_id not in self.campaigns:
            raise HTTPException(status_code=404, detail="Campaña no encontrada")
        
        self.campaigns[campaign_id]['estado'] = status
        self.campaigns[campaign_id]['updated_at'] = datetime.now().isoformat()
        return self.campaigns[campaign_id]
    
    # INTEGRACIONES
    async def save_integration(self, client_id: str, data: IntegrationRequest) -> Dict:
        integration_id = f"int_{data.platform}_{client_id}"
        integration = {
            'id': integration_id,
            'client_id': client_id,
            'platform': data.platform,
            'access_token': data.access_token,
            'configuracion': data.configuracion,
            'estado': 'connected',
            'connected_at': datetime.now().isoformat()
        }
        self.integrations[integration_id] = integration
        return integration
    
    async def get_integration(self, client_id: str, platform: str) -> Optional[Dict]:
        for int_id, integration in self.integrations.items():
            if integration['client_id'] == client_id and integration['platform'] == platform:
                return integration
        return None
    
    async def list_integrations(self, client_id: str) -> List[Dict]:
        return [i for i in self.integrations.values() if i['client_id'] == client_id]
    
    # ACTIVACIONES
    async def log_activation(self, client_id: str, campaign_id: str, 
                            workflow_type: str, resultado: Dict) -> Dict:
        activation = {
            'id': f"act_{datetime.now().timestamp()}",
            'client_id': client_id,
            'campaign_id': campaign_id,
            'tipo': workflow_type,
            'estado': 'activated',
            'resultado': resultado,
            'created_at': datetime.now().isoformat()
        }
        self.activations.append(activation)
        return activation
    
    # MÉTRICAS
    async def save_metrics(self, campaign_id: str, metrics: Dict) -> Dict:
        if campaign_id not in self.metrics:
            self.metrics[campaign_id] = []
        
        metric_entry = {
            'campaign_id': campaign_id,
            'fecha': datetime.now().isoformat(),
            **metrics
        }
        self.metrics[campaign_id].append(metric_entry)
        return metric_entry
    
    async def get_metrics(self, campaign_id: str) -> List[Dict]:
        return self.metrics.get(campaign_id, [])

# Instancia global
db = InMemoryDB()

# ==================== DEPENDENCIAS ====================

async def get_db() -> InMemoryDB:
    return db

# ==================== ENDPOINTS - CLIENTES ====================

@app.post("/api/clients", response_model=ClientResponse, tags=["Clientes"])
async def create_client(
    request: CreateClientRequest,
    db: InMemoryDB = Depends(get_db)
):
    """Crear nuevo cliente"""
    try:
        client = await db.create_client(request)
        return ClientResponse(
            id=client['id'],
            nombre=client['nombre'],
            email=client['email'],
            tipo_negocio=client['tipo_negocio'],
            objetivo=client['objetivo'],
            publico_objetivo=client['publico_objetivo'],
            presupuesto=client['presupuesto'],
            created_at=client['created_at']
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/clients", tags=["Clientes"])
async def list_clients(db: InMemoryDB = Depends(get_db)):
    """Listar todos los clientes"""
    clients = await db.list_clients()
    return {
        'total': len(clients),
        'clientes': clients
    }

@app.get("/api/clients/{client_id}", tags=["Clientes"])
async def get_client(
    client_id: str,
    db: InMemoryDB = Depends(get_db)
):
    """Obtener cliente específico con historial"""
    client = await db.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Agregar campañas
    campaigns = await db.list_campaigns(client_id)
    
    return {
        'cliente': client,
        'campanas_totales': len(campaigns),
        'campanas_activas': len([c for c in campaigns if c['estado'] == 'active']),
        'presupuesto_invertido': sum(c['presupuesto'] for c in campaigns),
        'historial_campanas': campaigns
    }

@app.put("/api/clients/{client_id}", tags=["Clientes"])
async def update_client(
    client_id: str,
    request: UpdateClientRequest,
    db: InMemoryDB = Depends(get_db)
):
    """Actualizar cliente (para mejorar conocimiento)"""
    client = await db.update_client(client_id, request)
    return {'mensaje': 'Cliente actualizado', 'cliente': client}

# ==================== ENDPOINTS - CAMPAÑAS ====================

@app.post("/api/campaigns", tags=["Campañas"])
async def create_campaign(
    request: CreateCampaignRequest,
    background_tasks: BackgroundTasks,
    db: InMemoryDB = Depends(get_db)
):
    """Crear campaña y generar outputs de agentes"""
    
    # Validar cliente existe
    client = await db.get_client(request.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Crear ProfileCampaignBrief
    client_profile = ClientProfile(
        id=client['id'],
        nombre=client['nombre'],
        tipo_negocio=client['tipo_negocio'],
        objetivo=client['objetivo'],
        publico_objetivo=client['publico_objetivo'],
        presupuesto=client['presupuesto'],
        descripcion=client['descripcion'],
        created_at=client['created_at']
    )
    
    campaign_brief = CampaignBrief(
        client_id=request.client_id,
        nombre_campaña=request.nombre_campaña,
        objetivo_especifico=request.objetivo_especifico,
        canal_principal=request.canal_principal,
        duracion_semanas=request.duracion_semanas,
        presupuesto=request.presupuesto,
        target_metrics={},
        additional_context=request.additional_context or ""
    )
    
    # Generar campaña con agentes
    orchestrator = CampaignOrchestrator(client_profile)
    campaign_output = await orchestrator.generate_campaign(campaign_brief)
    output_dict = orchestrator.output_as_dict(campaign_output)
    
    # Guardar en BD
    campaign = await db.create_campaign(request, output_dict)
    
    return {
        'mensaje': '✅ Campaña generada exitosamente',
        'campaign_id': campaign['id'],
        'estado': 'draft',
        'outputs_agentes': {
            'strategy': output_dict['strategy'],
            'content': output_dict['content'],
            'design': output_dict['design'],
            'video': output_dict['video'],
            'ads': output_dict['ads'],
            'automation': output_dict['automation']
        }
    }

@app.get("/api/campaigns/{campaign_id}", tags=["Campañas"])
async def get_campaign(
    campaign_id: str,
    db: InMemoryDB = Depends(get_db)
):
    """Obtener campaña completa con todos los outputs"""
    campaign = await db.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    
    return {
        'campaña': {
            'id': campaign['id'],
            'nombre': campaign['nombre'],
            'estado': campaign['estado'],
            'presupuesto': campaign['presupuesto'],
            'created_at': campaign['created_at']
        },
        'outputs_agentes': campaign['output_agentes'],
        'feedback': campaign['feedback']
    }

@app.get("/api/clients/{client_id}/campaigns", tags=["Campañas"])
async def list_client_campaigns(
    client_id: str,
    db: InMemoryDB = Depends(get_db)
):
    """Listar campañas de un cliente"""
    campaigns = await db.list_campaigns(client_id)
    
    return {
        'total': len(campaigns),
        'campanas': [
            {
                'id': c['id'],
                'nombre': c['nombre'],
                'estado': c['estado'],
                'presupuesto': c['presupuesto'],
                'created_at': c['created_at']
            }
            for c in campaigns
        ]
    }

@app.put("/api/campaigns/{campaign_id}/approve", tags=["Campañas"])
async def approve_campaign(
    campaign_id: str,
    db: InMemoryDB = Depends(get_db)
):
    """Aprobar campaña (cambiar estado de draft a approved)"""
    campaign = await db.update_campaign_status(campaign_id, 'approved')
    return {'mensaje': 'Campaña aprobada', 'estado': campaign['estado']}

# ==================== ENDPOINTS - INTEGRACIONES ====================

@app.post("/api/integrations/{client_id}", tags=["Integraciones"])
async def setup_integration(
    client_id: str,
    request: IntegrationRequest,
    db: InMemoryDB = Depends(get_db)
):
    """Configurar integración con plataforma (Meta, Google, etc)"""
    
    # Validar cliente existe
    client = await db.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Guardar integración
    integration = await db.save_integration(client_id, request)
    
    return {
        'mensaje': f'✅ {request.platform} conectado',
        'integration_id': integration['id'],
        'platform': integration['platform'],
        'estado': integration['estado']
    }

@app.get("/api/clients/{client_id}/integrations", tags=["Integraciones"])
async def list_integrations(
    client_id: str,
    db: InMemoryDB = Depends(get_db)
):
    """Listar integraciones de un cliente"""
    integrations = await db.list_integrations(client_id)
    
    return {
        'total': len(integrations),
        'integraciones': [
            {
                'platform': i['platform'],
                'estado': i['estado'],
                'connected_at': i['connected_at']
            }
            for i in integrations
        ]
    }

# ==================== ENDPOINTS - ACTIVACIONES ====================

@app.post("/api/campaigns/{campaign_id}/activate", tags=["Activaciones"])
async def activate_workflow(
    campaign_id: str,
    request: ActivateWorkflowRequest,
    db: InMemoryDB = Depends(get_db)
):
    """Activar workflow (lanzar campaña a Meta, Google, etc)"""
    
    # Obtener campaña
    campaign = await db.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    
    # Obtener integración necesaria
    platform_map = {
        'facebook_ads': 'meta',
        'instagram_ads': 'meta',
        'google_ads': 'google',
        'email_campaign': 'email',
        'n8n_workflow': 'n8n'
    }
    
    platform = platform_map.get(request.workflow_type)
    if not platform:
        raise HTTPException(status_code=400, detail="Tipo de workflow inválido")
    
    integration = await db.get_integration(campaign['client_id'], platform)
    if not integration or integration['estado'] != 'connected':
        raise HTTPException(status_code=400, 
                          detail=f"{platform} no está conectado. Conecta primero en Integraciones.")
    
    # Simular activación (en producción, llamar APIs reales)
    activation_result = {
        'status': 'activated',
        'workflow_type': request.workflow_type,
        'platform': platform,
        'activated_at': datetime.now().isoformat(),
        'message': f'✅ {request.workflow_type} activado exitosamente'
    }
    
    # Registrar activación
    activation = await db.log_activation(
        campaign['client_id'],
        campaign_id,
        request.workflow_type,
        activation_result
    )
    
    # Cambiar estado a active
    campaign = await db.update_campaign_status(campaign_id, 'active')
    
    return {
        'mensaje': f'✅ {request.workflow_type} activado',
        'activation_id': activation['id'],
        'campaign_estado': campaign['estado'],
        'proximos_pasos': [
            'Monitorear métricas en dashboard',
            'Ver resultados en tiempo real',
            'Ajustar estrategia según ROI'
        ]
    }

# ==================== ENDPOINTS - FEEDBACK ====================

@app.post("/api/campaigns/{campaign_id}/feedback", tags=["Feedback"])
async def submit_feedback(
    campaign_id: str,
    request: ClientFeedbackRequest,
    db: InMemoryDB = Depends(get_db)
):
    """Enviar feedback sobre outputs de agente (para que mejore)"""
    
    campaign = await db.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    
    feedback_entry = {
        'agent_type': request.agent_type,
        'rating': request.rating,
        'comentario': request.comentario,
        'mejoras': request.mejoras_sugeridas,
        'created_at': datetime.now().isoformat()
    }
    
    campaign['feedback'].append(feedback_entry)
    
    return {
        'mensaje': '✅ Feedback registrado. Los agentes mejorarán con esta información',
        'feedback_id': len(campaign['feedback']),
        'agente_mejorado': request.agent_type
    }

# ==================== ENDPOINTS - MÉTRICAS ====================

@app.get("/api/campaigns/{campaign_id}/metrics", tags=["Métricas"])
async def get_campaign_metrics(
    campaign_id: str,
    db: InMemoryDB = Depends(get_db)
):
    """Obtener métricas de campaña (ROI, leads, CPA)"""
    
    metrics = await db.get_metrics(campaign_id)
    
    if not metrics:
        return {
            'campaign_id': campaign_id,
            'mensaje': 'Sin métricas aún. La campaña debe estar activa.',
            'metricas': []
        }
    
    # Calcular promedios
    latest = metrics[-1] if metrics else {}
    
    return {
        'campaign_id': campaign_id,
        'metricas_actuales': latest,
        'historico': metrics,
        'resumen': {
            'leads_totales': sum(m.get('leads_generados', 0) for m in metrics),
            'cpa_promedio': sum(m.get('cpa_actual', 0) for m in metrics) / len(metrics) if metrics else 0,
            'roi_promedio': sum(m.get('roi_actual', 0) for m in metrics) / len(metrics) if metrics else 0
        }
    }

# ==================== ENDPOINTS - HEALTH ====================

@app.get("/health", tags=["Health"])
async def health():
    """Verificar estado del API"""
    return {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'mensaje': '✅ API funcionando correctamente'
    }

@app.get("/", tags=["Info"])
async def root():
    """Información de API"""
    return {
        'nombre': 'Agencia Marketing IA API',
        'versión': '1.0.0',
        'descripción': 'Sistema de gestión de campañas con agentes IA',
        'documentación': '/docs',
        'status': 'En desarrollo'
    }

# ==================== ERROR HANDLERS ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': True,
            'detail': exc.detail,
            'timestamp': datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            'error': True,
            'detail': 'Error interno del servidor',
            'mensaje': str(exc),
            'timestamp': datetime.now().isoformat()
        }
    )

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
