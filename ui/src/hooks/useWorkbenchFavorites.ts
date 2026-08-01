import { usePersistentState } from './usePersistentState'

const STORAGE_KEY = 'nyxstrike_workbench_favorites'

export function useWorkbenchFavorites() {
  const [favorites, setFavorites] = usePersistentState<string[]>(STORAGE_KEY, [])

  function isFavorite(id: string): boolean {
    return favorites.includes(id)
  }

  function toggleFavorite(id: string) {
    setFavorites(prev => prev.includes(id) ? prev.filter(f => f !== id) : [...prev, id])
  }

  return { favorites, isFavorite, toggleFavorite }
}
