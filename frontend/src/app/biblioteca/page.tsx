"use client";

import React, { useState, useEffect, useTransition } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Breadcrumbs } from "@/components/navigation/Breadcrumbs";
import { aiService } from "@/services/aiService";
import {
  libraryService,
  CanonicalBook,
  DeepGuide,
  KnowledgeSearchResult,
  CuratedResource,
  CollectionItem,
} from "@/services/libraryService";
import { useAuth } from "@/hooks/useAuth";
import { MarkdownViewer } from "@/components/common/MarkdownViewer";
import {
  Search,
  BookOpen,
  Bookmark,
  FileText,
  ExternalLink,
  Loader2,
  Wand2,
  Award,
  PlusCircle,
  CheckCircle2,
  Clock,
  Save,
  ChevronRight,
  Filter,
  X,
  GraduationCap,
  Layers,
  StickyNote,
} from "lucide-react";

export default function BibliotecaPage() {
  const router = useRouter();
  const { user } = useAuth();
  const profileId = user?.profile_id;

  const [isGeneratingProblem, setIsGeneratingProblem] = useState(false);

  const handleGenerateProblemFromDoc = async (doc: { title: string; content?: string }) => {
    setIsGeneratingProblem(true);
    try {
      const res = await aiService.generateProblem({
        level: "Iniciante",
        concept: doc.title,
        theme: doc.title,
        learning_request: (doc.content || "").slice(0, 800),
      });
      if (res && res.id) {
        router.push(`/workspace?problem=${res.id}&mode=arena`);
      } else {
        router.push("/workspace?mode=arena");
      }
    } catch (err) {
      console.error("Falha ao gerar problema do estudo:", err);
      router.push("/workspace?mode=arena");
    } finally {
      setIsGeneratingProblem(false);
    }
  };

  // Active Tab
  const [activeTab, setActiveTab] = useState<"search" | "books" | "guides" | "collection">("search");

  // Search State
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTopic, setSelectedTopic] = useState<string>("all");
  const [searchResults, setSearchResults] = useState<KnowledgeSearchResult[]>([]);
  const [curatedResources, setCuratedResources] = useState<CuratedResource[]>([]);
  const [kbStats, setKbStats] = useState<any>(null);
  const [isSearching, setIsSearching] = useState(false);

  // Books & Guides State
  const [books, setBooks] = useState<CanonicalBook[]>([]);
  const [guides, setGuides] = useState<DeepGuide[]>([]);
  const [selectedBook, setSelectedBook] = useState<CanonicalBook | null>(null);
  const [selectedGuide, setSelectedGuide] = useState<DeepGuide | null>(null);

  // Reader Modal & Lateral Note
  const [readingDoc, setReadingDoc] = useState<{ title: string; content: string; id: string; source?: string } | null>(null);
  const [docNote, setDocNote] = useState("");
  const [docStatus, setDocStatus] = useState<"Quero estudar" | "Estudando" | "Estudado">("Estudando");
  const [noteSavedFeedback, setNoteSavedFeedback] = useState(false);

  // Collection State
  const [collectionItems, setCollectionItems] = useState<CollectionItem[]>([]);
  const [collectionTotal, setCollectionTotal] = useState(0);
  const [collectionFilterStatus, setCollectionFilterStatus] = useState("all");
  const [isPending, startTransition] = useTransition();

  const TOPIC_PRESETS = [
    { id: "all", label: "Todos os Assuntos" },
    { id: "grafos", label: "Grafos & Árvores" },
    { id: "dp", label: "Programação Dinâmica" },
    { id: "matematica", label: "Teoria dos Números" },
    { id: "estruturas", label: "Estruturas de Dados" },
    { id: "busca", label: "Busca Binária & Dois Ponteiros" },
  ];

  // Initial Data Fetch
  useEffect(() => {
    // Carrega livros canônicos e guias
    libraryService.getBooksAndGuides().then((data) => {
      setBooks(data.books || []);
      setGuides(data.guides || []);
    }).catch(console.error);

    // Carrega busca padrão inicial e estatísticas do acervo
    libraryService.searchKnowledge("", undefined, 12).then((data) => {
      setCuratedResources(data.curated_resources || []);
      setKbStats(data.stats);
    }).catch(console.error);
  }, []);

  // Debounced Search Effect
  useEffect(() => {
    const timer = setTimeout(() => {
      if (!searchQuery && selectedTopic === "all") return;
      setIsSearching(true);
      const queryParam = selectedTopic !== "all" && !searchQuery ? selectedTopic : searchQuery;
      libraryService.searchKnowledge(queryParam, selectedTopic !== "all" ? selectedTopic : undefined, 15)
        .then((data) => {
          setSearchResults(data.results || []);
          if (data.curated_resources?.length > 0) {
            setCuratedResources(data.curated_resources);
          }
        })
        .finally(() => setIsSearching(false));
    }, 350);

    return () => clearTimeout(timer);
  }, [searchQuery, selectedTopic]);

  // Load User Collection when Tab is Selected
  useEffect(() => {
    if (activeTab === "collection") {
      libraryService.getCollection({
        profile_id: profileId,
        status: collectionFilterStatus === "all" ? undefined : collectionFilterStatus,
      }).then((data) => {
        setCollectionItems(data.items || []);
        setCollectionTotal(data.total || 0);
      }).catch(console.error);
    }
  }, [activeTab, profileId, collectionFilterStatus]);

  // Open Document in Reader
  const handleOpenDoc = async (id: string, titleFallback?: string) => {
    try {
      const res = await libraryService.getDocument(id);
      if (res.type === "guide") {
        const g = res.data as DeepGuide;
        const markdown = `# ${g.title}\n\n**Autor:** ${g.author} · **Tempo:** ~${g.minutes} min · **Pré-requisitos:** ${g.prerequisites}\n\n` +
          g.sections.map((s) => `## ${s.title}\n\n${s.body}`).join("\n\n") +
          `\n\n## Exercícios Fixadores\n\n` +
          g.exercises.map((e, i) => `**${i + 1}.** ${e.prompt}\n\n*Resposta:* ${e.answer}`).join("\n\n");
        setReadingDoc({ id: g.id, title: g.title, content: markdown, source: "AutoTutor CP Guia" });
      } else {
        const d = res.data;
        setReadingDoc({ id: d.id, title: d.title || titleFallback || "Artigo", content: d.content || d.body || "", source: d.source });
      }
      setDocNote("");
      setDocStatus("Estudando");
    } catch (e) {
      console.error("Falha ao abrir documento:", e);
    }
  };

  // Save Note & Status
  const handleSaveNote = async () => {
    if (!readingDoc) return;
    try {
      await libraryService.saveState({
        profile_id: profileId,
        item_id: readingDoc.id,
        status: docStatus,
        note: docNote,
      });
      setNoteSavedFeedback(true);
      setTimeout(() => setNoteSavedFeedback(false), 2500);
    } catch (e) {
      console.error("Erro ao salvar anotação:", e);
    }
  };

  const breadcrumbs = [
    { label: "Dashboard", href: "/" },
    { label: "Biblioteca & Conhecimento" },
  ];

  return (
    <>
      <main className="flex-1 flex flex-col min-w-0 pb-20 lg:pb-8">
        <header className="px-6 py-4 border-b border-border bg-card/40 backdrop-blur-sm sticky top-0 z-30">
          <Breadcrumbs items={breadcrumbs} />
        </header>

        <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 space-y-6">
          {/* Header Title Banner */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <BookOpen className="w-7 h-7 text-primary" />
                <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
                  Biblioteca & Acervo de Conhecimento
                </h1>
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Artigos indexados, livros clássicos de maratona (CLRS, CP4, CPH) e anotações pessoais de estudo.
                {kbStats?.documents && (
                  <span className="ml-2 inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20">
                    <Layers className="w-3 h-3" />
                    {kbStats.documents.toLocaleString()} documentos indexados
                  </span>
                )}
              </p>
            </div>

            <Link
              href="/lab"
              className="inline-flex items-center justify-center gap-2 px-3.5 py-1.5 rounded-md text-xs font-medium bg-blue-600 text-white hover:bg-blue-500 transition-colors shadow-sm"
            >
              <Wand2 className="w-3.5 h-3.5" />
              <span>Gerar Estudo no Lab</span>
            </Link>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-2 border-b border-border overflow-x-auto pb-1 text-xs font-medium">
            <button
              type="button"
              onClick={() => setActiveTab("search")}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-t-lg transition-all border-b-2 whitespace-nowrap ${
                activeTab === "search"
                  ? "border-primary text-primary font-bold bg-primary/5"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              <Search className="w-4 h-4" />
              <span>Pesquisa RAG & Acervo</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("books")}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-t-lg transition-all border-b-2 whitespace-nowrap ${
                activeTab === "books"
                  ? "border-primary text-primary font-bold bg-primary/5"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              <GraduationCap className="w-4 h-4" />
              <span>Livros Canônicos ({books.length})</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("guides")}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-t-lg transition-all border-b-2 whitespace-nowrap ${
                activeTab === "guides"
                  ? "border-primary text-primary font-bold bg-primary/5"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Guias de Aprofundamento ({guides.length})</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("collection")}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-t-lg transition-all border-b-2 whitespace-nowrap ${
                activeTab === "collection"
                  ? "border-primary text-primary font-bold bg-primary/5"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              <Bookmark className="w-4 h-4" />
              <span>Minha Coleção & Anotações ({collectionTotal})</span>
            </button>
          </div>

          {/* TAB 1: SEARCH & RAG CORPUS */}
          {activeTab === "search" && (
            <div className="space-y-6">
              {/* Search Bar & Topic Pills */}
              <div className="p-4 rounded-2xl border border-border bg-card/60 space-y-4">
                <div className="relative">
                  <Search className="w-5 h-5 text-muted-foreground absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Buscar conceitos, algoritmos, CP-Algorithms, CSES (ex: BFS, Dijkstra, Bitmask DP, Segment Tree)..."
                    className="w-full pl-11 pr-4 py-3 bg-secondary/50 border border-border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 text-foreground"
                  />
                  {searchQuery && (
                    <button
                      type="button"
                      onClick={() => setSearchQuery("")}
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>

                <div className="flex items-center gap-2 flex-wrap text-xs">
                  <span className="text-muted-foreground font-semibold flex items-center gap-1 mr-1">
                    <Filter className="w-3.5 h-3.5" />
                    Tópicos:
                  </span>
                  {TOPIC_PRESETS.map((t) => (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => setSelectedTopic(t.id)}
                      className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                        selectedTopic === t.id
                          ? "bg-primary text-primary-foreground shadow-sm"
                          : "bg-secondary/70 hover:bg-secondary text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Search Loading Indicator */}
              {isSearching && (
                <div className="flex items-center justify-center gap-2 py-8 text-sm text-slate-400">
                  <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
                  <span>Consultando acervo indexado de programação competitiva...</span>
                </div>
              )}

              {/* RAG Results Grid */}
              {searchResults.length > 0 && (
                <div className="space-y-3">
                  <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-primary" />
                    Resultados no Acervo ({searchResults.length})
                  </h2>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {searchResults.map((res) => (
                      <div
                        key={res.id + (res.heading || "")}
                        className="p-4 rounded-xl border border-border bg-card/70 hover:border-primary/50 transition-all flex flex-col justify-between space-y-3 group"
                      >
                        <div className="space-y-1.5">
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-secondary text-muted-foreground truncate">
                              {res.source || "Acervo CP"}
                            </span>
                            {res.score && (
                              <span className="text-[10px] text-muted-foreground font-mono">
                                Score: {res.score.toFixed(1)}
                              </span>
                            )}
                          </div>
                          <h3 className="text-sm font-bold text-foreground group-hover:text-primary transition-colors line-clamp-2">
                            {res.title}
                          </h3>
                          {res.heading && (
                            <p className="text-xs font-semibold text-muted-foreground line-clamp-1">
                              Secção: {res.heading}
                            </p>
                          )}
                          {res.excerpt && (
                            <p className="text-xs text-muted-foreground/90 line-clamp-3 leading-relaxed">
                              {res.excerpt}
                            </p>
                          )}
                        </div>

                        <div className="flex items-center justify-between pt-2 border-t border-border/50 text-xs">
                          <button
                            type="button"
                            onClick={() => handleOpenDoc(res.id, res.title)}
                            className="text-primary hover:underline font-semibold flex items-center gap-1"
                          >
                            <span>Ler Artigo Completo</span>
                            <ChevronRight className="w-3.5 h-3.5" />
                          </button>
                          {res.url && res.url.startsWith("http") && (
                            <a
                              href={res.url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-muted-foreground hover:text-foreground flex items-center gap-1 text-[11px]"
                            >
                              <span>Origem</span>
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Curated Resources Shelf */}
              {curatedResources.length > 0 && (
                <div className="space-y-3 pt-4">
                  <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                    <Award className="w-4 h-4 text-amber-500" />
                    Referências Curadas & Vídeos Recomendados
                  </h2>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {curatedResources.map((item, idx) => (
                      <div
                        key={idx + item.url}
                        className="p-4 rounded-xl border border-border bg-card/50 flex flex-col justify-between space-y-3"
                      >
                        <div className="space-y-1.5">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-primary/10 text-primary">
                              {item.kind || "Referência"}
                            </span>
                            <span className="text-[10px] text-muted-foreground">{item.publisher}</span>
                          </div>
                          <h4 className="text-sm font-bold text-foreground line-clamp-2">{item.title}</h4>
                          {item.summary && (
                            <p className="text-xs text-muted-foreground line-clamp-2">{item.summary}</p>
                          )}
                        </div>

                        <div className="flex items-center justify-between pt-2 border-t border-border/50 text-xs">
                          <a
                            href={item.url}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 text-primary hover:underline font-semibold"
                          >
                            <span>Acessar Link ↗</span>
                          </a>
                          {item.verification && (
                            <span className="text-[10px] text-muted-foreground truncate max-w-[150px]">
                              {item.verification}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: CANONICAL BOOKS */}
          {activeTab === "books" && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {books.map((book) => (
                  <div
                    key={book.id}
                    className="p-5 rounded-2xl border border-border bg-card/70 hover:border-primary/50 transition-all flex flex-col justify-between space-y-4"
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-primary/10 text-primary font-bold">
                          {book.edition}
                        </span>
                        {book.open_access ? (
                          <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/20">
                            Acesso Aberto
                          </span>
                        ) : (
                          <span className="text-[10px] text-muted-foreground">{book.publisher}</span>
                        )}
                      </div>

                      <h3 className="text-base font-bold text-foreground leading-snug">{book.title}</h3>
                      <p className="text-xs text-muted-foreground font-medium">
                        {book.authors?.join(", ")}
                      </p>
                      <p className="text-xs text-muted-foreground/90 leading-relaxed line-clamp-3">
                        {book.overview}
                      </p>
                    </div>

                    <div className="space-y-3 pt-3 border-t border-border/60">
                      <button
                        type="button"
                        onClick={() => setSelectedBook(book)}
                        className="w-full py-2 px-3 rounded-xl text-xs font-semibold bg-secondary hover:bg-secondary/80 text-foreground transition-colors flex items-center justify-center gap-1.5"
                      >
                        <Layers className="w-3.5 h-3.5 text-primary" />
                        <span>Ver Tópicos por Capítulo</span>
                      </button>

                      {book.url && (
                        <a
                          href={book.url}
                          target="_blank"
                          rel="noreferrer"
                          className="w-full py-2 px-3 rounded-xl text-xs font-semibold border border-border hover:bg-card text-muted-foreground hover:text-foreground transition-colors flex items-center justify-center gap-1.5"
                        >
                          <span>Página Oficial do Livro</span>
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: DEEP GUIDES */}
          {activeTab === "guides" && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {guides.map((guide) => (
                <div
                  key={guide.id}
                  className="p-5 rounded-2xl border border-border bg-card/70 hover:border-primary/50 transition-all flex flex-col justify-between space-y-4"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-primary" />
                        ~{guide.minutes} min
                      </span>
                      <span className="font-mono text-[10px]">{guide.author}</span>
                    </div>

                    <h3 className="text-base font-bold text-foreground leading-snug">{guide.title}</h3>
                    <p className="text-xs text-muted-foreground">
                      <strong className="text-foreground">Pré-requisitos:</strong> {guide.prerequisites}
                    </p>

                    <div className="text-xs text-muted-foreground/80 space-y-1 pt-1">
                      <span className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground block">
                        Seções do Guia:
                      </span>
                      {guide.sections.slice(0, 3).map((s, idx) => (
                        <div key={idx} className="flex items-center gap-1.5 truncate">
                          <span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
                          <span className="truncate">{s.title}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="pt-3 border-t border-border/60">
                    <button
                      type="button"
                      onClick={() => handleOpenDoc(guide.id, guide.title)}
                      className="w-full py-2.5 px-4 rounded-xl text-xs font-bold bg-primary text-primary-foreground hover:bg-primary/90 transition-all flex items-center justify-center gap-2 shadow-sm"
                    >
                      <BookOpen className="w-4 h-4" />
                      <span>Abrir Guia & Exercícios</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 4: MY COLLECTION & NOTES */}
          {activeTab === "collection" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between gap-4 p-4 rounded-xl border border-border bg-card/50">
                <span className="text-xs text-muted-foreground font-medium">
                  {collectionTotal} materiais didáticos e estudos salvos vinculados ao seu perfil.
                </span>

                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">Status:</span>
                  <select
                    value={collectionFilterStatus}
                    onChange={(e) => setCollectionFilterStatus(e.target.value)}
                    className="bg-secondary border border-border rounded-lg text-xs px-2.5 py-1 text-foreground focus:outline-none"
                  >
                    <option value="all">Todos os Status</option>
                    <option value="Quero estudar">Quero estudar</option>
                    <option value="Estudando">Estudando</option>
                    <option value="Estudado">Estudado</option>
                  </select>
                </div>
              </div>

              {collectionItems.length === 0 ? (
                <div className="p-12 text-center border border-dashed border-border rounded-2xl space-y-3">
                  <Bookmark className="w-8 h-8 text-muted-foreground mx-auto" />
                  <p className="text-sm font-semibold text-foreground">Sua coleção está pronta para receber materiais.</p>
                  <p className="text-xs text-muted-foreground max-w-sm mx-auto">
                    Gere uma apostila personalizada no Laboratório IA ou salve artigos consultados na pesquisa do acervo.
                  </p>
                  <Link
                    href="/lab"
                    className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-md text-xs font-medium bg-blue-600 text-white hover:bg-blue-500 mt-2 transition-colors"
                  >
                    <PlusCircle className="w-3.5 h-3.5" />
                    <span>Criar Material no Lab</span>
                  </Link>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {collectionItems.map((item) => (
                    <div
                      key={item.id}
                      className="p-4 rounded-xl border border-border bg-card/70 flex flex-col justify-between space-y-3"
                    >
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-primary/10 text-primary font-bold">
                            {item.kind}
                          </span>
                          <span
                            className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                              item.status === "Estudado"
                                ? "bg-emerald-500/10 text-emerald-400"
                                : item.status === "Estudando"
                                ? "bg-amber-500/10 text-amber-400"
                                : "bg-secondary text-muted-foreground"
                            }`}
                          >
                            {item.status}
                          </span>
                        </div>

                        <h4 className="text-sm font-bold text-foreground">{item.title}</h4>
                        <p className="text-[11px] text-muted-foreground font-mono">{item.time}</p>

                        {item.note && (
                          <div className="p-2.5 rounded-lg bg-secondary/50 border border-border text-xs text-muted-foreground flex items-start gap-2">
                            <StickyNote className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
                            <p className="line-clamp-2">{item.note}</p>
                          </div>
                        )}
                      </div>

                      <div className="pt-2 border-t border-border/50 flex items-center justify-between text-xs">
                        <button
                          type="button"
                          onClick={() => {
                            const content =
                              item.payload?.markdown ||
                              item.payload?.content ||
                              item.payload?.statement ||
                              (typeof item.payload === "string" ? item.payload : JSON.stringify(item.payload, null, 2));
                            setReadingDoc({
                              id: item.id,
                              title: item.title,
                              content: content,
                              source: "Minha Coleção",
                            });
                            setDocNote(item.note || "");
                            setDocStatus(item.status);
                          }}
                          className="text-primary hover:underline font-semibold flex items-center gap-1"
                        >
                          <span>Abrir Estudo</span>
                          <ChevronRight className="w-3.5 h-3.5" />
                        </button>

                        <button
                          type="button"
                          disabled={isGeneratingProblem}
                          onClick={() => {
                            const content =
                              item.payload?.markdown ||
                              item.payload?.content ||
                              item.payload?.statement ||
                              item.title;
                            handleGenerateProblemFromDoc({ title: item.title, content });
                          }}
                          className="text-muted-foreground hover:text-primary text-[11px] font-medium flex items-center gap-1 transition-colors"
                        >
                          <Wand2 className="w-3 h-3 text-primary" />
                          <span>Gerar Questão</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* MODAL 1: BOOK CHAPTER DETAILS */}
      {selectedBook && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-card border border-border rounded-2xl max-w-2xl w-full p-6 space-y-4 max-h-[85vh] flex flex-col shadow-2xl">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div>
                <h3 className="text-base font-bold text-foreground">{selectedBook.title}</h3>
                <span className="text-xs text-muted-foreground">{selectedBook.authors?.join(", ")} · {selectedBook.edition}</span>
              </div>
              <button
                type="button"
                onClick={() => setSelectedBook(null)}
                className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 pr-1 text-xs">
              <p className="text-muted-foreground leading-relaxed">{selectedBook.overview}</p>

              <h4 className="font-bold text-foreground uppercase tracking-wider text-[11px] pt-2">
                Mapeamento de Tópicos por Capítulo:
              </h4>

              <div className="space-y-2">
                {Object.entries(selectedBook.topics || {}).map(([key, desc]) => (
                  <div key={key} className="p-3 rounded-xl bg-secondary/40 border border-border space-y-1">
                    <span className="font-bold uppercase text-[10px] text-primary">{key}</span>
                    <p className="text-muted-foreground text-xs leading-relaxed">{desc}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-3 border-t border-border flex items-center justify-between">
              {selectedBook.url && (
                <a
                  href={selectedBook.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
                >
                  <span>Abrir Editora ↗</span>
                </a>
              )}
              <button
                type="button"
                onClick={() => setSelectedBook(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-secondary hover:bg-secondary/80 text-foreground"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 2: FULL ARTICLE READER + LATERAL NOTEPAD */}
      {readingDoc && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-2 sm:p-4">
          <div className="bg-card border border-border rounded-2xl max-w-5xl w-full h-[90vh] flex flex-col shadow-2xl overflow-hidden">
            {/* Reader Header */}
            <div className="px-6 py-4 border-b border-border bg-card/60 flex items-center justify-between">
              <div className="min-w-0 pr-4">
                <span className="text-[10px] font-mono uppercase text-primary px-2 py-0.5 rounded bg-primary/10">
                  {readingDoc.source || "Artigo de Maratona"}
                </span>
                <h3 className="text-base sm:text-lg font-bold text-foreground truncate mt-1">
                  {readingDoc.title}
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  disabled={isGeneratingProblem}
                  onClick={() => handleGenerateProblemFromDoc(readingDoc)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-primary text-primary-foreground hover:bg-primary-hover shadow-sm transition-all shrink-0 disabled:opacity-50"
                >
                  <Wand2 className={`w-3.5 h-3.5 ${isGeneratingProblem ? "animate-spin" : ""}`} />
                  <span>{isGeneratingProblem ? "Gerando..." : "Gerar Questão deste estudo →"}</span>
                </button>
                <button
                  type="button"
                  onClick={() => setReadingDoc(null)}
                  className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary shrink-0"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Split View: Reader Text (Left) + Notepad (Right) */}
            <div className="flex-1 flex flex-col md:flex-row min-h-0 overflow-hidden">
              {/* Document Text Body */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4 border-b md:border-b-0 md:border-r border-border">
                <MarkdownViewer content={readingDoc.content} />
              </div>

              {/* Lateral Notepad per Student */}
              <div className="w-full md:w-80 p-5 bg-card/30 flex flex-col justify-between shrink-0 space-y-4 overflow-y-auto">
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <StickyNote className="w-4 h-4 text-primary" />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-foreground">
                      Meu Andamento & Anotações
                    </h4>
                  </div>

                  {/* Status Selector */}
                  <div className="space-y-1.5">
                    <label className="text-[11px] text-muted-foreground font-medium">Situação:</label>
                    <select
                      value={docStatus}
                      onChange={(e) => setDocStatus(e.target.value as any)}
                      className="w-full bg-secondary border border-border rounded-xl text-xs px-3 py-2 text-foreground focus:outline-none"
                    >
                      <option value="Quero estudar">Quero estudar</option>
                      <option value="Estudando">Estudando</option>
                      <option value="Estudado">Estudado</option>
                    </select>
                  </div>

                  {/* Student Notepad */}
                  <div className="space-y-1.5">
                    <label className="text-[11px] text-muted-foreground font-medium">Minhas Notas:</label>
                    <textarea
                      value={docNote}
                      onChange={(e) => setDocNote(e.target.value)}
                      placeholder="Anote dúvidas, ideias de implementação, atalhos de complexidade ou observações para revisão..."
                      rows={10}
                      maxLength={4000}
                      className="w-full bg-secondary/50 border border-border rounded-xl p-3 text-xs text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 resize-none"
                    />
                    <span className="text-[10px] text-muted-foreground block text-right">
                      {docNote.length}/4000 caracteres
                    </span>
                  </div>
                </div>

                <div className="space-y-2 pt-2 border-t border-border">
                  <button
                    type="button"
                    onClick={handleSaveNote}
                    className="w-full py-2.5 px-4 rounded-xl text-xs font-bold bg-primary text-primary-foreground hover:bg-primary/90 transition-all flex items-center justify-center gap-2 shadow-sm"
                  >
                    <Save className="w-3.5 h-3.5" />
                    <span>Salvar Anotação</span>
                  </button>

                  <button
                    type="button"
                    disabled={isGeneratingProblem}
                    onClick={() => handleGenerateProblemFromDoc(readingDoc)}
                    className="w-full py-2.5 px-4 rounded-xl text-xs font-bold border border-primary/40 text-primary hover:bg-primary/10 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    <Wand2 className={`w-3.5 h-3.5 ${isGeneratingProblem ? "animate-spin" : ""}`} />
                    <span>{isGeneratingProblem ? "Gerando Questão..." : "Praticar Questão no Juiz →"}</span>
                  </button>

                  {noteSavedFeedback && (
                    <p className="text-[11px] text-emerald-400 text-center flex items-center justify-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Anotação e status salvos com sucesso!
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
