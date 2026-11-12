"use client";

import React, { useState, useEffect } from "react";
import { configService, LlmConfig } from "@/services/configService";
import { aiService } from "@/services/aiService";
import {
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Key,
  Cpu,
  ShieldCheck,
  Save,
  Check,
  X,
} from "lucide-react";

interface AiConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const PROVIDER_PRESETS: Record<string, string[]> = {
  Gemini: ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash"],
  OpenAI: ["gpt-4o", "gpt-4o-mini"],
  DeepSeek: ["deepseek-chat", "deepseek-coder"],
  Qwen: ["qwen-plus", "qwen-turbo"],
  Ollama: ["qwen2.5-coder:7b", "deepseek-r1:7b", "llama3.1:8b"],
};

export function AiConfigModal({ isOpen, onClose }: AiConfigModalProps) {
  const [config, setConfig] = useState<LlmConfig | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string>("Gemini");
  const [apiKeyInput, setApiKeyInput] = useState<string>("");
  const [selectedModel, setSelectedModel] = useState<string>("gemini-3.5-flash");
  const [pingStatus, setPingStatus] = useState<any | null>(null);
  const [isTesting, setIsTesting] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen) {
      configService.getConfig().then((data) => {
        setConfig(data);
        const prov = data.provider || "Gemini";
        setSelectedProvider(prov);
        const mod = data.model && data.model !== "gemini-2.5-flash"
          ? data.model
          : (prov === "Gemini" ? "gemini-3.5-flash" : "qwen2.5-coder:7b");
        setSelectedModel(mod);
      }).catch(console.error);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleProviderChange = (prov: string) => {
    setSelectedProvider(prov);
    setPingStatus(null);
    const presets = PROVIDER_PRESETS[prov] || [];
    if (presets.length > 0) {
      setSelectedModel(presets[0]);
    }
  };

  const handlePing = async () => {
    setIsTesting(true);
    setPingStatus(null);
    try {
      const res = await configService.ping({
        provider: selectedProvider,
        api_key: apiKeyInput || undefined,
        model: selectedModel || undefined,
      });
      setPingStatus(res);
    } catch (err: any) {
      setPingStatus({
        ok: false,
        provider: selectedProvider,
        status: "credentials_error",
        status_code: 400,
        latency_ms: 0,
        message: err.message || "Falha de conexão com o provedor de IA.",
      });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await aiService.saveLlmConfig({
        provider: selectedProvider,
        api_key: apiKeyInput || undefined,
        model: selectedModel || undefined,
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);
      const updated = await configService.getConfig();
      setConfig(updated);
    } catch (e) {
      console.error(e);
    } finally {
      setIsSaving(false);
    }
  };

  const getStatusBadge = () => {
    if (!pingStatus) return null;
    const isOk = pingStatus.ok;
    const code = pingStatus.status_code || (isOk ? 200 : 400);

    let title = `[Falha · ${code}]`;
    if (isOk) title = `[Conectado · 200 OK${pingStatus.latency_ms ? ` · ${pingStatus.latency_ms}ms` : ""}]`;
    else if (code === 404) title = "[Modelo Indisponível · 404]";
    else if (code === 429) title = "[Cota Excedida · 429]";
    else if (code === 503) title = "[Sobrecarga Temporária · 503]";
    else if (code === 401 || code === 403) title = "[Falha de Autenticação · 401]";

    return (
      <div
        className={`p-3 rounded-md border text-xs flex items-start gap-2.5 animate-in fade-in-0 duration-150 ${
          isOk
            ? "bg-emerald-950/60 border-emerald-800/60 text-emerald-300"
            : "bg-red-950/60 border-red-800/60 text-red-300"
        }`}
      >
        {isOk ? (
          <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5 text-emerald-400" />
        ) : (
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-red-400" />
        )}
        <div className="space-y-1 flex-1">
          <div className="flex items-center justify-between">
            <span className="font-mono font-medium text-[11px]">{title}</span>
            <span className="text-[10px] text-slate-400 font-mono">{pingStatus.provider}</span>
          </div>
          <p className="text-[11px] leading-relaxed text-slate-300">{pingStatus.message}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in-0 duration-150">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-lg shadow-xl overflow-hidden flex flex-col">
        {/* Header Sóbrio */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded bg-slate-800 text-slate-300 border border-slate-700/60">
              <Cpu className="w-4 h-4 text-blue-400" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100">Configuração do Provedor de IA</h3>
              <p className="text-[11px] text-slate-400">Gerencie chaves de API e modelos para geração de conteúdo e tutoria</p>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Fechar modal"
            className="text-slate-400 hover:text-slate-200 p-1 rounded hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        <div className="p-4 space-y-3.5">
          {/* Provider Selection */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-300">Provedor / Motor</label>
            <div className="grid grid-cols-5 gap-1.5">
              {["Gemini", "OpenAI", "DeepSeek", "Qwen", "Ollama"].map((prov) => (
                <button
                  key={prov}
                  type="button"
                  onClick={() => handleProviderChange(prov)}
                  className={`px-2 py-1.5 rounded text-xs font-medium border transition-colors text-center ${
                    selectedProvider === prov
                      ? "bg-slate-800 text-white border-slate-700 shadow-sm"
                      : "bg-slate-950/60 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800"
                  }`}
                >
                  {prov}
                </button>
              ))}
            </div>
          </div>

          {/* Model Name & Presets */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium text-slate-300">Modelo Selecionado</label>
              <span className="text-[10px] text-slate-500 font-mono">Presets rápidos abaixo</span>
            </div>
            <input
              type="text"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              placeholder="ex: gemini-3.5-flash, qwen2.5-coder:7b"
              className="w-full px-3 py-1.5 rounded bg-slate-950/70 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-slate-700 font-mono"
            />
            {/* Presets de modelos recomendados */}
            <div className="flex items-center gap-1.5 pt-1 overflow-x-auto no-scrollbar">
              <span className="text-[10px] text-slate-500">Recomendados:</span>
              {(PROVIDER_PRESETS[selectedProvider] || []).map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setSelectedModel(m)}
                  className={`px-2 py-0.5 rounded text-[10px] font-mono border transition-colors ${
                    selectedModel === m
                      ? "bg-blue-950/80 text-blue-300 border-blue-800/80"
                      : "bg-slate-800/60 text-slate-400 border-slate-700/40 hover:text-slate-200 hover:bg-slate-800"
                  }`}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>

          {/* API Key */}
          {selectedProvider !== "Ollama" ? (
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                  <Key className="w-3.5 h-3.5 text-slate-400" />
                  <span>Chave de API ({selectedProvider})</span>
                </label>
                {config?.masked_key && (
                  <span className="text-[10px] text-slate-400 font-mono">
                    Atual: {config.masked_key}
                  </span>
                )}
              </div>
              <input
                type="password"
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                placeholder="Insira nova chave ou deixe em branco para manter a atual"
                className="w-full px-3 py-1.5 rounded bg-slate-950/70 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-slate-700 font-mono"
              />
              <p className="text-[10px] text-slate-500">
                A chave é protegida e persistida no backend headless sem exposição no cliente.
              </p>
            </div>
          ) : (
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800 text-xs text-slate-400 space-y-1">
              <span className="font-medium text-slate-200 block">Ollama (Daemon Local)</span>
              <p className="text-[11px] leading-relaxed text-slate-400">
                Executando localmente na porta 11434. Não requer chave de API externa.
              </p>
            </div>
          )}

          {/* Ping Status Visual Badge */}
          {getStatusBadge()}
        </div>

        {/* Footer Actions */}
        <div className="p-3 border-t border-slate-800 bg-slate-900 flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
            <span>Handshake (1 token)</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handlePing}
              disabled={isTesting}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium bg-slate-800 text-slate-200 hover:bg-slate-700 hover:text-white border border-slate-700/60 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isTesting ? "animate-spin" : ""}`} />
              <span>{isTesting ? "Testando..." : "Testar Conexão / Ping"}</span>
            </button>

            <button
              type="button"
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded text-xs font-medium bg-blue-600 text-white hover:bg-blue-500 shadow-sm transition-colors disabled:opacity-50"
            >
              {saveSuccess ? (
                <>
                  <Check className="w-3.5 h-3.5" />
                  <span>Salvo!</span>
                </>
              ) : (
                <>
                  <Save className="w-3.5 h-3.5" />
                  <span>{isSaving ? "Salvando..." : "Salvar Configuração"}</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
