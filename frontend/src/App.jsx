import { useState } from 'react'
import { useFetch } from './hooks/useFetch'
import { api } from './api/client'
import styles from './App.module.css'

const TABS = ['training', 'testing']

function downloadJson(data, filename) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export default function App() {
  const [tab, setTab] = useState('training')

  const training = useFetch(() => api.trainingData(), [])
  const testing = useFetch(() => api.testingData(), [])

  const active = tab === 'training' ? training : testing
  const { data, loading, error } = active

  const columns = data?.length ? Object.keys(data[0]) : []

  return (
    <div className={styles.layout}>
      <div className={styles.toolbar}>
        <div className={styles.tabs}>
          {TABS.map(t => (
            <button
              key={t}
              className={`${styles.tab} ${tab === t ? styles.active : ''}`}
              onClick={() => setTab(t)}
            >
              {t}
            </button>
          ))}
        </div>
        <div className={styles.right}>
          {data && (
            <span className={styles.count}>{data.length} rows</span>
          )}
          <button
            className={styles.download}
            disabled={!data}
            onClick={() => downloadJson(data, `${tab}-data.json`)}
          >
            ↓ download
          </button>
        </div>
      </div>

      <div className={styles.tableWrap}>
        {loading && <div className={styles.state}>loading...</div>}
        {error && <div className={`${styles.state} ${styles.err}`}>{error}</div>}
        {!loading && !error && !data?.length && (
          <div className={styles.state}>no data</div>
        )}
        {!loading && !error && data?.length > 0 && (
          <table className={styles.table}>
            <thead>
              <tr>
                {columns.map(col => <th key={col}>{col}</th>)}
              </tr>
            </thead>
            <tbody>
              {data.map((row, i) => (
                <tr key={i}>
                  {columns.map(col => (
                    <td key={col}>
                      {row[col] == null ? <span className={styles.null}>—</span> : String(row[col])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
