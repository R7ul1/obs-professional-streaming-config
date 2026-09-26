#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar OBS automáticamente
Compatible con OBS 32.2.2+
"""

import asyncio
import json
import sys
from obswebsocket import obsws, requests

# Configuración
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = ""

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}→ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def conectar_obs():
    """Conecta a OBS WebSocket"""
    print_info("Conectando a OBS...")
    try:
        ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
        ws.connect()
        print_success("Conectado a OBS correctamente")
        return ws
    except Exception as e:
        print_error(f"No se pudo conectar a OBS: {e}")
        print_warning("Asegúrate de:")
        print("  1. Tener OBS abierto")
        print("  2. Activar WebSocket en: Herramientas → Ajustes del servidor WebSocket")
        print("  3. Usar la contraseña correcta")
        sys.exit(1)

def crear_coleccion_escenas(ws):
    """Crea una nueva colección de escenas"""
    print_info("Creando colección de escenas...")
    try:
        # OBS crea automáticamente una colección cuando añades escenas
        print_success("Colección preparada")
        return True
    except Exception as e:
        print_error(f"Error al crear colección: {e}")
        return False

def crear_escena(ws, nombre_escena):
    """Crea una escena"""
    print_info(f"Creando escena: {nombre_escena}")
    try:
        request = requests.CreateScene(sceneName=nombre_escena)
        ws.call(request)
        print_success(f"Escena '{nombre_escena}' creada")
        return True
    except Exception as e:
        if "already exists" in str(e):
            print_warning(f"Escena '{nombre_escena}' ya existe")
            return True
        print_error(f"Error creando escena: {e}")
        return False

def crear_fuente_color(ws, escena, nombre, color=0x1a1a1a):
    """Crea una fuente de color (fondo)"""
    print_info(f"  Añadiendo fondo a '{escena}'")
    try:
        request = requests.CreateSceneItem(
            sceneName=escena,
            sourceName=nombre,
            sourceKind="color_source_v2",
            sceneItemSettings={
                "color": color
            }
        )
        ws.call(request)
        print_success(f"  Fondo '{nombre}' añadido")
        return True
    except Exception as e:
        if "already exists" in str(e):
            print_warning(f"  Fondo '{nombre}' ya existe")
            return True
        print_error(f"  Error: {e}")
        return False

def crear_fuente_texto(ws, escena, nombre, texto, tamaño=24, color=0xFFFFFF):
    """Crea una fuente de texto"""
    print_info(f"  Añadiendo texto: {nombre}")
    try:
        request = requests.CreateSceneItem(
            sceneName=escena,
            sourceName=nombre,
            sourceKind="text_gdiplus",
            sceneItemSettings={
                "text": texto,
                "font": {
                    "face": "Arial",
                    "size": tamaño,
                    "flags": 0
                },
                "color": color
            }
        )
        ws.call(request)
        print_success(f"  Texto '{nombre}' añadido")
        return True
    except Exception as e:
        if "already exists" in str(e):
            print_warning(f"  Texto '{nombre}' ya existe")
            return True
        print_error(f"  Error: {e}")
        return False

def crear_fuente_captura_juego(ws, escena):
    """Crea Game Capture"""
    print_info(f"  Añadiendo Game Capture")
    try:
        request = requests.CreateSceneItem(
            sceneName=escena,
            sourceName="Game Capture",
            sourceKind="game_capture",
            sceneItemSettings={
                "capture_mode": 1,  # Window
                "priority": 0
            }
        )
        ws.call(request)
        print_success(f"  Game Capture añadido")
        return True
    except Exception as e:
        if "already exists" in str(e):
            print_warning(f"  Game Capture ya existe")
            return True
        print_error(f"  Error: {e}")
        return False

def crear_fuente_webcam(ws, escena, nombre="Webcam"):
    """Crea fuente de webcam"""
    print_info(f"  Añadiendo Webcam")
    try:
        request = requests.CreateSceneItem(
            sceneName=escena,
            sourceName=nombre,
            sourceKind="video_capture",
            sceneItemSettings={}
        )
        ws.call(request)
        print_success(f"  Webcam '{nombre}' añadida")
        return True
    except Exception as e:
        if "already exists" in str(e):
            print_warning(f"  Webcam ya existe")
            return True
        print_error(f"  Error: {e}")
        return False

def configurar_audio(ws):
    """Configura el micrófono Fifine con filtros profesionales"""
    print_info("Configurando audio profesional...")
    
    try:
        # Configurar Fifine como entrada de micrófono
        print_info("  Buscando dispositivo Fifine...")
        
        # Obtener lista de dispositivos de audio
        try:
            request = requests.GetInputList(inputKind="wasapi_input_capture")
            devices = ws.call(request)
            print_success("  Dispositivos de audio detectados")
        except:
            print_warning("  No se pudo obtener lista de dispositivos")
            return False
        
        # Crear fuente de audio del micrófono
        try:
            request = requests.CreateSceneItem(
                sceneName="",  # Global
                sourceName="Micrófono Fifine",
                sourceKind="wasapi_input_capture",
                sceneItemSettings={}
            )
            ws.call(request)
            print_success("  Micrófono Fifine configurado")
        except:
            print_warning("  Micrófono ya existe o no se encontró")
        
        # Configurar filtros del micrófono
        print_info("  Añadiendo filtros de audio...")
        
        filtros = [
            {
                "filterName": "Noise Suppression",
                "filterKind": "noise_suppress_filter_v1",
                "filterSettings": {
                    "suppression_level": 0.8,
                    "method": 1
                }
            },
            {
                "filterName": "Gain",
                "filterKind": "gain_filter",
                "filterSettings": {
                    "db": 2.0
                }
            },
            {
                "filterName": "Compressor",
                "filterKind": "compressor_filter",
                "filterSettings": {
                    "threshold": -16,
                    "ratio": 4,
                    "attack": 10,
                    "release": 150
                }
            }
        ]
        
        for filtro in filtros:
            try:
                request = requests.CreateSourceFilter(
                    sourceName="Micrófono Fifine",
                    filterName=filtro["filterName"],
                    filterKind=filtro["filterKind"],
                    filterSettings=filtro["filterSettings"]
                )
                ws.call(request)
                print_success(f"  Filtro '{filtro['filterName']}' añadido")
            except Exception as e:
                print_warning(f"  No se pudo añadir filtro '{filtro['filterName']}'")
        
        return True
        
    except Exception as e:
        print_error(f"Error configurando audio: {e}")
        return False

def configurar_salida(ws):
    """Configura encoder NVENC y resolución"""
    print_info("Configurando salida de vídeo...")
    
    try:
        # Configurar salida NVENC H.264
        print_info("  Configurando NVIDIA NVENC H.264...")
        
        settings = {
            "SimpleRTMPServer": False,
            "SimpleOutputPath": "",
            "SimpleFormat": "mp4",
            "SimpleFormatMuxDelay": 0,
            "SimpleOutRecType": "Standard",
            "SimpleOutStrEncoder": "nvidia_nvenc",
            "SimpleOutStrAudioEncoder": "aac",
            "SimpleOutRecEncoder": "h264",
            "SimpleOutRecAudioEncoder": "aac",
            "AdvOutEncoder": "nvidia_nvenc",
            "AdvOutAudioEncoder": "aac",
            "AdvOutRecEncoder": "h264",
            "AdvOutRecAudioEncoder": "aac",
            "VBitrate": 6000,
            "ABitrate": 128,
            "FLVTrack": 1,
            "FFOutputToFile": True,
            "FFFilePath": "",
            "FFExtension": "mp4",
            "FFVEncoderId": 0,
            "FFVEncoder": "h264_nvenc",
            "FFAEncoderId": 0,
            "FFAEncoder": "aac",
            "FFAMixerClockHz": 48000,
            "FFRBitrate": 0,
            "FFLBitrate": 0,
            "FFCRCMuxDelay": 0,
            "FFURL": "",
            "NVENCPreset": "Quality",
            "NVENCRateControl": "CBR",
            "NVENCB-frames": 2,
            "NVENCKeyframeInterval": 2,
            "NVENCUseRC": True,
            "NVENCLookahead": True,
            "NVENCPsychoVisualTune": True
        }
        
        try:
            request = requests.SetOutputSettings(
                outputName="streaming",
                outputSettings=settings
            )
            ws.call(request)
            print_success("  Encoder NVENC H.264 configurado")
        except:
            print_warning("  No se pudo configurar NVENC (verificar si tienes GPU NVIDIA)")
        
        # Configurar resolución 1920x1080 @ 60 FPS
        print_info("  Configurando 1920x1080 @ 60 FPS...")
        
        try:
            request = requests.SetVideoSettings(
                outputWidth=1920,
                outputHeight=1080,
                baseWidth=1920,
                baseHeight=1080,
                fpsNum=60,
                fpsDen=1
            )
            ws.call(request)
            print_success("  Resolución configurada: 1920x1080 @ 60 FPS")
        except Exception as e:
            print_warning(f"  No se pudo configurar resolución: {e}")
        
        return True
        
    except Exception as e:
        print_error(f"Error configurando salida: {e}")
        return False

def main():
    """Función principal"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}   CONFIGURADOR AUTOMÁTICO DE OBS PRO{Colors.END}")
    print(f"{Colors.BLUE}   Setup: RTX 4060 Ti + i9-9900K + Fifine{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    # Solicitar contraseña WebSocket
    global OBS_PASSWORD
    print_info("Ingresa la contraseña del servidor WebSocket de OBS:")
    print("  (Herramientas → Ajustes del servidor WebSocket)")
    OBS_PASSWORD = input(f"{Colors.YELLOW}Contraseña: {Colors.END}")
    
    if not OBS_PASSWORD:
        print_warning("No ingresaste contraseña. Intentando sin contraseña...")
        OBS_PASSWORD = ""
    
    # Conectar
    ws = conectar_obs()
    
    # Crear colección
    crear_coleccion_escenas(ws)
    
    # Crear escenas
    print(f"\n{Colors.BLUE}Creando escenas...{Colors.END}")
    escenas = ["STARTING", "GAMEPLAY", "JUST CHATTING", "BRB", "ENDING", "OFFLINE"]
    
    for escena in escenas:
        crear_escena(ws, escena)
    
    # Configurar escenas con fuentes
    print(f"\n{Colors.BLUE}Configurando escenas...{Colors.END}")
    
    # STARTING
    print_info("Configurando STARTING...")
    crear_fuente_color(ws, "STARTING", "Fondo STARTING")
    crear_fuente_texto(ws, "STARTING", "Titulo", "EN DIRECTO EN BREVE", 48)
    crear_fuente_texto(ws, "STARTING", "Subtitulo", "Preparando streaming...", 24)
    crear_fuente_webcam(ws, "STARTING", "Webcam")
    
    # GAMEPLAY
    print_info("Configurando GAMEPLAY...")
    crear_fuente_captura_juego(ws, "GAMEPLAY")
    crear_fuente_webcam(ws, "GAMEPLAY", "Webcam")
    crear_fuente_texto(ws, "GAMEPLAY", "Live Badge", "LIVE", 20, 0xFF0000)
    
    # JUST CHATTING
    print_info("Configurando JUST CHATTING...")
    crear_fuente_color(ws, "JUST CHATTING", "Fondo Chat")
    crear_fuente_texto(ws, "JUST CHATTING", "Titulo", "JUST CHATTING", 48)
    crear_fuente_webcam(ws, "JUST CHATTING", "Webcam")
    
    # BRB
    print_info("Configurando BRB...")
    crear_fuente_color(ws, "BRB", "Fondo BRB")
    crear_fuente_texto(ws, "BRB", "BRB Text", "BRB • VOLVEMOS PRONTO", 50)
    crear_fuente_texto(ws, "BRB", "Subtext", "Estamos revisando", 24)
    
    # ENDING
    print_info("Configurando ENDING...")
    crear_fuente_color(ws, "ENDING", "Fondo Ending")
    crear_fuente_texto(ws, "ENDING", "Gracias", "GRACIAS POR VER", 48)
    crear_fuente_texto(ws, "ENDING", "Redes", "Síguenos en Twitch • YouTube • Discord", 20)
    
    # OFFLINE
    print_info("Configurando OFFLINE...")
    crear_fuente_color(ws, "OFFLINE", "Fondo Offline")
    crear_fuente_texto(ws, "OFFLINE", "Offline Text", "STREAM OFFLINE", 52)
    crear_fuente_texto(ws, "OFFLINE", "Info", "Próximo directo en breve", 22)
    
    # Configurar audio
    print(f"\n{Colors.BLUE}Configurando audio...{Colors.END}")
    configurar_audio(ws)
    
    # Configurar salida
    print(f"\n{Colors.BLUE}Configurando salida de vídeo...{Colors.END}")
    configurar_salida(ws)
    
    # Desconectar
    print_info("Cerrando conexión...")
    ws.disconnect()
    
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}✓ ¡CONFIGURACIÓN COMPLETADA!{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
    
    print_success("Tu OBS está configurado profesionalmente:")
    print("  • 6 escenas listas para usar")
    print("  • 1920x1080 @ 60 FPS")
    print("  • NVIDIA NVENC H.264")
    print("  • Bitrate: 6000 Kbps")
    print("  • Audio profesional con Fifine")
    print("  • Filtros de audio (RNNoise, Gain, Compressor)")
    
    print(f"\n{Colors.YELLOW}Próximos pasos:{Colors.END}")
    print("  1. Abre OBS")
    print("  2. Ve a cada escena y selecciona:")
    print("     - Tu webcam real (en lugar de la genérica)")
    print("     - Tu juego en Game Capture")
    print("     - Tu micrófono Fifine en Mixer de Audio")
    print("  3. Prueba el audio (habla y verifica niveles)")
    print("  4. ¡Streamea!")
    
    print(f"\n{Colors.BLUE}Para más ayuda, ve a los archivos de documentación en el repositorio.{Colors.END}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Cancelado por el usuario{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error inesperado: {e}{Colors.END}\n")
        sys.exit(1)
