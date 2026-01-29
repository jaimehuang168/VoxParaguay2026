'use client';

import { useState, useEffect } from 'react';
import { ChevronRight, Check, SkipForward } from 'lucide-react';

interface SurveyQuestion {
  id: string;
  orden: number;
  texto: string;
  tipo: 'escala' | 'opcion_multiple' | 'texto_libre' | 'si_no';
  opciones?: string[];
  peso: number;
  condicion?: {
    si_respuesta: string;
    ir_a: string;
  };
}

interface VisualSurveyScriptProps {
  conversationId: string;
}

// Mock survey script
const mockQuestions: SurveyQuestion[] = [
  {
    id: 'q1',
    orden: 1,
    texto: '¿Cómo calificaría los servicios de salud en su comunidad?',
    tipo: 'escala',
    peso: 1.5,
  },
  {
    id: 'q2',
    orden: 2,
    texto: '¿Cuál es su principal preocupación actualmente?',
    tipo: 'opcion_multiple',
    opciones: ['Salud', 'Educación', 'Seguridad', 'Empleo', 'Economía'],
    peso: 1.0,
  },
  {
    id: 'q3',
    orden: 3,
    texto: '¿Tiene algún comentario adicional?',
    tipo: 'texto_libre',
    peso: 0.5,
  },
];

// Emoji scale for visual buttons (1-5)
const emojiScale = ['😞', '😕', '😐', '🙂', '😃'];

export function VisualSurveyScript({ conversationId }: VisualSurveyScriptProps) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [isComplete, setIsComplete] = useState(false);

  // Offline storage
  useEffect(() => {
    // Load from localStorage if exists
    const saved = localStorage.getItem(`survey_${conversationId}`);
    if (saved) {
      const parsed = JSON.parse(saved);
      setAnswers(parsed.answers || {});
      setCurrentQuestionIndex(parsed.currentIndex || 0);
    }
  }, [conversationId]);

  // Save to localStorage on change
  useEffect(() => {
    localStorage.setItem(
      `survey_${conversationId}`,
      JSON.stringify({
        answers,
        currentIndex: currentQuestionIndex,
        lastUpdated: new Date().toISOString(),
      })
    );
  }, [answers, currentQuestionIndex, conversationId]);

  const currentQuestion = mockQuestions[currentQuestionIndex];

  const handleAnswer = (value: any) => {
    const questionId = currentQuestion.id;
    setAnswers({ ...answers, [questionId]: value });

    // Check for conditional branching
    if (currentQuestion.condicion) {
      const targetQuestion = mockQuestions.findIndex(
        (q) => q.id === currentQuestion.condicion?.ir_a
      );
      if (targetQuestion !== -1 && value === currentQuestion.condicion.si_respuesta) {
        setCurrentQuestionIndex(targetQuestion);
        return;
      }
    }

    // Move to next question
    if (currentQuestionIndex < mockQuestions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      setIsComplete(true);
    }
  };

  const handleSkip = () => {
    if (currentQuestionIndex < mockQuestions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      setIsComplete(true);
    }
  };

  if (isComplete) {
    return (
      <div className="p-6">
        <div className="text-center py-8">
          <div className="text-6xl mb-4">✅</div>
          <h3 className="text-xl font-semibold text-green-600">
            Encuesta Completada
          </h3>
          <p className="text-gray-500 mt-2">
            {Object.keys(answers).length} de {mockQuestions.length} preguntas
            respondidas
          </p>
          <button
            onClick={() => {
              setCurrentQuestionIndex(0);
              setIsComplete(false);
            }}
            className="mt-4 text-primary-500 hover:underline"
          >
            Ver respuestas
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4">
      {/* Progress */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-500 mb-2">
          <span>Pregunta {currentQuestionIndex + 1} de {mockQuestions.length}</span>
          <span>Peso: {currentQuestion.peso}x</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary-500 h-2 rounded-full transition-all"
            style={{
              width: `${((currentQuestionIndex + 1) / mockQuestions.length) * 100}%`,
            }}
          />
        </div>
      </div>

      {/* Question */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {currentQuestion.texto}
        </h3>

        {/* Scale Question (Emoji Buttons) */}
        {currentQuestion.tipo === 'escala' && (
          <div className="grid grid-cols-5 gap-2">
            {emojiScale.map((emoji, index) => (
              <button
                key={index}
                onClick={() => handleAnswer(index + 1)}
                className={`survey-emoji-btn ${
                  answers[currentQuestion.id] === index + 1 ? 'selected' : ''
                }`}
              >
                {emoji}
                <p className="text-xs text-gray-500 mt-1">{index + 1}</p>
              </button>
            ))}
          </div>
        )}

        {/* Multiple Choice */}
        {currentQuestion.tipo === 'opcion_multiple' && (
          <div className="space-y-2">
            {currentQuestion.opciones?.map((option) => (
              <button
                key={option}
                onClick={() => handleAnswer(option)}
                className={`w-full p-4 text-left rounded-xl border-2 transition ${
                  answers[currentQuestion.id] === option
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-primary-300'
                }`}
              >
                <span className="flex items-center justify-between">
                  {option}
                  {answers[currentQuestion.id] === option && (
                    <Check className="w-5 h-5 text-primary-500" />
                  )}
                </span>
              </button>
            ))}
          </div>
        )}

        {/* Free Text */}
        {currentQuestion.tipo === 'texto_libre' && (
          <div>
            <textarea
              className="w-full border rounded-xl p-4 h-32 focus:ring-2 focus:ring-primary-500 focus:outline-none"
              placeholder="Escriba la respuesta del encuestado..."
              value={answers[currentQuestion.id] || ''}
              onChange={(e) =>
                setAnswers({ ...answers, [currentQuestion.id]: e.target.value })
              }
            />
            <button
              onClick={() => handleAnswer(answers[currentQuestion.id])}
              disabled={!answers[currentQuestion.id]}
              className="mt-4 w-full bg-primary-500 text-white py-3 rounded-xl hover:bg-primary-600 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              Continuar <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        )}

        {/* Yes/No */}
        {currentQuestion.tipo === 'si_no' && (
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => handleAnswer('si')}
              className={`p-6 text-2xl rounded-xl border-2 transition ${
                answers[currentQuestion.id] === 'si'
                  ? 'border-green-500 bg-green-50'
                  : 'border-gray-200 hover:border-green-300'
              }`}
            >
              👍 Sí
            </button>
            <button
              onClick={() => handleAnswer('no')}
              className={`p-6 text-2xl rounded-xl border-2 transition ${
                answers[currentQuestion.id] === 'no'
                  ? 'border-red-500 bg-red-50'
                  : 'border-gray-200 hover:border-red-300'
              }`}
            >
              👎 No
            </button>
          </div>
        )}
      </div>

      {/* Skip button */}
      <button
        onClick={handleSkip}
        className="w-full text-gray-500 py-2 flex items-center justify-center gap-2 hover:text-gray-700"
      >
        <SkipForward className="w-4 h-4" />
        Saltar pregunta
      </button>

      {/* Navigation dots */}
      <div className="flex justify-center gap-1 mt-6">
        {mockQuestions.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentQuestionIndex(index)}
            className={`w-2 h-2 rounded-full transition ${
              index === currentQuestionIndex
                ? 'bg-primary-500'
                : answers[mockQuestions[index].id]
                ? 'bg-green-500'
                : 'bg-gray-300'
            }`}
          />
        ))}
      </div>
    </div>
  );
}
