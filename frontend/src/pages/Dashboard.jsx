import { useState } from 'react'
import { api } from '../api/client'
import { useFetch } from '../hooks/useFetch'
import { Card } from '../components/Card'
import { StatusPill } from '../components/StatusPill'
import { DataTable } from '../components/DataTable'
import styles from './Dashboard.module.css'

const STACK = [
  { label: 'nodes', value: '3' },
  { label: 'bronze', value: 'minio' },
  { label: 'silver / gold', value: 'clickhouse' },
  { label: 'orchestration', value: 'k3s + airflow' },
]

const DATA_TABS = ['training', 'testing']

export function Dashboard() {
  const [activeTab, setActiveTab] = useState('training')

  const health = useFetch(() => api.health())
  const trainingData = useFetch(() => api.trainingData(), [])
  const testingData = useFetch(() => api.testingData(), [])

  const tableData = activeTab === 'training' ? trainingData : testingData

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <div>
          <div className={styles.breadcrumb}>
            <a href="http://dilleystone.com:8000/docs" target="_blank" rel="noreferrer">
              dilleystone.com:8000
            </a>
            &nbsp;/&nbsp;fantasy-football
          </div>
          <h1 className={styles.h1}>fantasy football</h1>
        </div>
        <StatusPill online={!health.loading && !health.error} />
      </header>

      <div className={styles.stackStrip}>
        {STACK.map(({ label, value }) => (
          <div key={label} className={styles.stackItem}>
            <div className={styles.stackLabel}>{label}</div>
            <div className={styles.stackValue}>{value}</div>
          </div>
        ))}
      </div>

      <div className={styles.grid}>

        <Card title="data explorer" full>
          <div className={styles.tabs}>
            {DATA_TABS.map(tab => (
              <button
                key={tab}
                className={`${styles.tab} ${activeTab === tab ? styles.tabActive : ''}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))}
            <button
              className={styles.refetch}
              onClick={tableData.refetch}
              disabled={tableData.loading}
            >
              ↻ refresh
            </button>
          </div>
          <DataTable
            data={tableData.data}
            loading={tableData.loading}
            error={tableData.error}
          />
        </Card>

        <Card title="api endpoints">
          {[
            { method: 'GET', path: '/training-data', desc: 'gold layer · causal features' },
            { method: 'GET', path: '/testing-data', desc: 'gold layer · no causal info' },
            { method: 'POST', path: '/evaluate', desc: 'score model predictions' },
          ].map(({ method, path, desc }) => (
            <div key={path} className={styles.endpoint}>
              <span className={`${styles.method} ${styles[method.toLowerCase()]}`}>{method}</span>
              <span className={styles.epPath}>{path}</span>
              <span className={styles.epDesc}>{desc}</span>
            </div>
          ))}
        </Card>

        <Card title="goals">
          {[
            { n: '01', title: 'learn rust', body: 'rewrite the fastapi service as the first real project' },
            { n: '02', title: 'build e2e', body: 'own the full stack: ingestion, storage, features, modeling, serving' },
            { n: '03', title: 'win fantasy', body: 'the whole point' },
          ].map(({ n, title, body }) => (
            <div key={n} className={styles.goal}>
              <span className={styles.goalNum}>{n}</span>
              <span className={styles.goalText}><strong>{title}</strong> — {body}</span>
            </div>
          ))}
        </Card>

      </div>

      <footer className={styles.footer}>
        <span className={styles.footerMono}>medallion architecture · minio → clickhouse → fastapi</span>
        <a href="http://dilleystone.com:8000/docs" target="_blank" rel="noreferrer" className={styles.footerLink}>
          docs ↗
        </a>
      </footer>
    </div>
  )
}
