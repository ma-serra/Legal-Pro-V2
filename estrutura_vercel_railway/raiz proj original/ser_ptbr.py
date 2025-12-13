"""
Speech Emotion Recognition (SER) para Português do Brasil
Versão simplificada com fallback para análise textual quando modelos não estão disponíveis
"""

import os
import json
import re
import requests
from typing import List, Dict, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SERPTBR:
    """
    Classe para análise de emoções em áudio português brasileiro
    Usa análise textual como fallback quando modelos de áudio não estão disponíveis
    """
    
    def __init__(self):
        """
        Inicializa o sistema de reconhecimento de emoções
        """
        self.model_available = False
        
        # Labels de emoções padrão
        self.emotion_labels_pt = {
            "anger": "raiva",
            "disgust": "nojo", 
            "fear": "medo",
            "happiness": "alegria",
            "neutral": "neutro",
            "sadness": "tristeza",
            "surprise": "surpresa"
        }
        
        # Palavras-chave para detecção de emoções em texto
        self.emotion_keywords = {
            "alegria": ["feliz", "alegre", "contente", "satisfeito", "otimo", "excelente", "maravilhoso", "bom", "legal"],
            "tristeza": ["triste", "melancólico", "deprimido", "chateado", "ruim", "péssimo", "horrível"],
            "raiva": ["irritado", "furioso", "bravo", "nervoso", "zangado", "revoltado", "indignado"],
            "medo": ["medo", "receio", "preocupado", "ansioso", "apreensivo", "temeroso"],
            "surpresa": ["surpreso", "espantado", "admirado", "impressionado", "chocado"],
            "nojo": ["nojento", "repugnante", "asqueroso", "desagradável"],
            "neutro": ["normal", "ok", "bem", "regular", "comum"]
        }
        
        logger.info("SER PT-BR inicializado com análise textual")
        
    def _analyze_text_emotion(self, text: str) -> Dict[str, Any]:
        """
        Analisa emoção baseada no texto usando palavras-chave e OpenAI API
        """
        text_lower = text.lower()
        emotion_scores = {}
        
        # Análise por palavras-chave
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            emotion_scores[emotion] = score
        
        # Normalizar scores
        total_score = sum(emotion_scores.values())
        if total_score > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] = emotion_scores[emotion] / total_score
        else:
            emotion_scores["neutro"] = 1.0
        
        # Encontrar emoção predominante
        top_emotion = max(emotion_scores, key=emotion_scores.get)
        top_score = emotion_scores[top_emotion]
        
        # Se score muito baixo, usar OpenAI para análise mais precisa
        if top_score < 0.3:
            try:
                openai_result = self._analyze_with_openai(text)
                if openai_result:
                    return openai_result
            except Exception as e:
                logger.warning(f"Análise OpenAI falhou: {e}")
        
        # Converter scores para percentual
        emotion_scores_pct = {k: round(v * 100, 2) for k, v in emotion_scores.items()}
        
        return {
            "emotion_top": top_emotion,
            "emotion_top_pt": top_emotion,
            "score_top": round(top_score, 2),
            "scores_pt": emotion_scores_pct
        }
    
    def _analyze_with_openai(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Análise de emoção usando OpenAI API para maior precisão
        """
        try:
            openai_api_key = os.environ.get('OPENAI_API_KEY')
            if not openai_api_key:
                return None
            
            headers = {
                'Authorization': f'Bearer {openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "Analise a emoção do texto em português e responda em JSON: {'emocao': 'alegria/tristeza/raiva/medo/surpresa/nojo/neutro', 'confianca': 0.0-1.0, 'scores': {'alegria': 0-100, 'tristeza': 0-100, 'raiva': 0-100, 'medo': 0-100, 'surpresa': 0-100, 'nojo': 0-100, 'neutro': 0-100}}"},
                    {"role": "user", "content": f"Analise a emoção deste texto: '{text[:200]}'"}
                ],
                "response_format": {"type": "json_object"},
                "max_tokens": 150
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = json.loads(result['choices'][0]['message']['content'])
                
                return {
                    "emotion_top": analysis.get('emocao', 'neutro'),
                    "emotion_top_pt": analysis.get('emocao', 'neutro'),
                    "score_top": analysis.get('confianca', 0.5),
                    "scores_pt": analysis.get('scores', {"neutro": 50})
                }
                
        except Exception as e:
            logger.warning(f"OpenAI emotion analysis failed: {e}")
            return None
    
    def _extract_audio_features(self, audio_path: str, start_time: Optional[float] = None, end_time: Optional[float] = None) -> Dict[str, Any]:
        """
        Extrai características básicas do áudio (duração, presença de som)
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            start_time: Tempo inicial em segundos (opcional)
            end_time: Tempo final em segundos (opcional)
            
        Returns:
            Dict com características básicas do áudio
        """
        try:
            import wave
            import struct
            
            # Tentar abrir como WAV
            try:
                with wave.open(audio_path, 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    sample_rate = wav_file.getframerate()
                    duration = frames / sample_rate
                    
                    return {
                        "duration": duration,
                        "has_audio": duration > 0,
                        "sample_rate": sample_rate
                    }
            except:
                # Fallback: usar informações básicas do arquivo
                file_size = os.path.getsize(audio_path)
                estimated_duration = max(1.0, file_size / 32000)  # Estimativa básica
                
                return {
                    "duration": estimated_duration,
                    "has_audio": file_size > 1000,  # Assumir que tem áudio se arquivo > 1KB
                    "sample_rate": 16000
                }
                
        except Exception as e:
            logger.warning(f"Erro ao extrair características do áudio: {e}")
            return {
                "duration": 1.0,
                "has_audio": True,
                "sample_rate": 16000
            }
    
    def analyze_clip(self, audio_path: str, start_time: Optional[float] = None, end_time: Optional[float] = None, text: str = "") -> Dict[str, Any]:
        """
        Analisa emoção em um clipe de áudio usando análise textual como fallback
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            start_time: Tempo inicial em segundos (opcional)
            end_time: Tempo final em segundos (opcional)
            text: Texto transcrito para análise de emoção (fallback)
            
        Returns:
            Dict com emoção principal, score e scores detalhados
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_path}")
        
        try:
            # Extrair características básicas do áudio
            audio_features = self._extract_audio_features(audio_path, start_time, end_time)
            
            # Se não há áudio válido, retornar neutro
            if not audio_features["has_audio"]:
                logger.warning(f"Segmento sem áudio válido: {start_time}-{end_time}")
                return {
                    "emotion_top": "neutro",
                    "emotion_top_pt": "neutro",
                    "score_top": 0.5,
                    "scores_pt": {"neutro": 50}
                }
            
            # Usar análise textual como método principal
            if text and text.strip():
                emotion_result = self._analyze_text_emotion(text.strip())
                logger.info(f"Emoção detectada por texto: {emotion_result['emotion_top_pt']} ({emotion_result['score_top']:.2f})")
                return emotion_result
            
            # Fallback: emoção neutra para áudio sem texto
            return {
                "emotion_top": "neutro",
                "emotion_top_pt": "neutro",
                "score_top": 0.6,
                "scores_pt": {"neutro": 60, "alegria": 20, "surpresa": 20}
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de emoção: {e}")
            return {
                "emotion_top": "neutro",
                "emotion_top_pt": "neutro", 
                "score_top": 0.5,
                "scores_pt": {"neutro": 50},
                "error": str(e)
            }
    
    def analyze_segments(self, audio_path: str, segments: List[Dict]) -> List[Dict]:
        """
        Analisa emoções para múltiplos segmentos do Whisper
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            segments: Lista de segmentos do Whisper com formato:
                     [{"start": float, "end": float, "text": str}, ...]
        
        Returns:
            Lista de segmentos com emoções adicionadas
        """
        if not segments:
            logger.warning("Lista de segmentos vazia")
            return []
        
        logger.info(f"Analisando emoções para {len(segments)} segmentos...")
        
        enriched_segments = []
        
        for i, segment in enumerate(segments):
            try:
                start_time = segment.get("start", 0.0)
                end_time = segment.get("end", start_time + 1.0)
                text = segment.get("text", "")
                
                # Análise de emoção para o segmento (passa o texto para análise)
                emotion_result = self.analyze_clip(audio_path, start_time, end_time, text)
                
                # Enriquecer segmento
                enriched_segment = {
                    "start": start_time,
                    "end": end_time,
                    "text": text,
                    "emotion_top": emotion_result["emotion_top_pt"],
                    "emotion_top_pt": emotion_result["emotion_top_pt"],
                    "score_top": emotion_result["score_top"],
                    "scores_pt": emotion_result["scores_pt"]
                }
                
                # Adicionar campos originais que possam existir
                for key, value in segment.items():
                    if key not in enriched_segment:
                        enriched_segment[key] = value
                
                enriched_segments.append(enriched_segment)
                
                logger.info(f"Segmento {i+1}/{len(segments)}: {emotion_result['emotion_top_pt']} ({emotion_result['score_top']:.2f})")
                
            except Exception as e:
                logger.error(f"Erro no segmento {i}: {e}")
                # Manter segmento original com emoção neutra
                enriched_segment = segment.copy()
                enriched_segment.update({
                    "emotion_top": "neutro",
                    "emotion_top_pt": "neutro",
                    "score_top": 0.5,
                    "scores_pt": {"neutro": 50},
                    "error": str(e)
                })
                enriched_segments.append(enriched_segment)
        
        logger.info(f"Análise de emoções concluída para {len(enriched_segments)} segmentos")
        return enriched_segments

def test_ser():
    """
    Função de teste para o módulo SER
    """
    try:
        ser = SERPTBR()
        print("SER PT-BR inicializado com sucesso!")
        print(f"Device usado: {ser.device}")
        print(f"Labels disponíveis: {list(ser.emotion_labels_pt.values())}")
        
        # Teste com arquivo de exemplo se disponível
        test_files = ["exemplo.wav", "test.wav", "audio_test.wav"]
        
        for test_file in test_files:
            if os.path.exists(test_file):
                print(f"\nTestando com {test_file}...")
                result = ser.analyze_clip(test_file)
                print(f"Emoção detectada: {result['emotion_top_pt']} ({result['score_top']:.2f})")
                print(f"Scores: {result['scores_pt']}")
                break
        else:
            print("Nenhum arquivo de teste encontrado. Teste manual necessário.")
            
    except Exception as e:
        print(f"Erro no teste: {e}")

if __name__ == "__main__":
    test_ser()