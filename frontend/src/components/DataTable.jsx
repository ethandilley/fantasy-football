import styles from './DataTable.module.css'

export function DataTable({ data, loading, error }) {
  if (loading) return <div className={styles.state}>loading...</div>
  if (error) return <div className={`${styles.state} ${styles.error}`}>{error}</div>
  if (!data?.length) return <div className={styles.state}>no data</div>

  const columns = Object.keys(data[0])

  return (
    <div className={styles.wrap}>
      <table className={styles.table}>
        <thead>
          <tr>
            {columns.map(col => (
              <th key={col} className={styles.th}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} className={styles.tr}>
              {columns.map(col => (
                <td key={col} className={styles.td}>
                  {row[col] == null ? <span className={styles.null}>—</span> : String(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
