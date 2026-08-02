import { useCallback } from 'react'
import type { CSSProperties } from 'react'

type StaggerStyle = CSSProperties & { '--stagger-index'?: number }

/**
 * Returns a function that produces the inline style + class name for the
 * Nth item in a staggered-reveal list. Pair with the `.stagger-item`
 * keyframe in animations.css: `<div className="stagger-item" style={staggerStyle(i)}>`.
 */
export function useStaggerReveal() {
  return useCallback((index: number): StaggerStyle => ({
    '--stagger-index': index,
  }), [])
}
