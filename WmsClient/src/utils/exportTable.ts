export interface ExportColumn<T> {
  key: keyof T | string
  label: string
  format?: (row: T) => string | number
}

function cellValue<T>(row: T, column: ExportColumn<T>) {
  if (column.format) return column.format(row)
  const value = (row as Record<string, unknown>)[column.key as string]
  if (value == null) return ''
  return value
}

function escapeCsv(value: string | number) {
  const text = String(value)
  if (/[",\n\r]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`
  }
  return text
}

function escapeXml(value: string | number) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function downloadBlob(filename: string, blob: Blob) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

export function exportCsv<T>(filename: string, columns: ExportColumn<T>[], rows: T[]) {
  const header = columns.map((column) => escapeCsv(column.label)).join(',')
  const body = rows.map((row) =>
    columns.map((column) => escapeCsv(cellValue(row, column))).join(','),
  )
  const content = `\uFEFF${[header, ...body].join('\n')}`
  downloadBlob(filename.endsWith('.csv') ? filename : `${filename}.csv`, new Blob([content], {
    type: 'text/csv;charset=utf-8;',
  }))
}

/** SpreadsheetML，Excel 可直接打开，无需额外依赖 */
export function exportExcel<T>(filename: string, columns: ExportColumn<T>[], rows: T[]) {
  const header = columns
    .map((column) => `<Cell><Data ss:Type="String">${escapeXml(column.label)}</Data></Cell>`)
    .join('')
  const body = rows.map((row) => {
    const cells = columns.map((column) => {
      const value = cellValue(row, column)
      const isNumber = typeof value === 'number' && Number.isFinite(value)
      return `<Cell><Data ss:Type="${isNumber ? 'Number' : 'String'}">${escapeXml(value)}</Data></Cell>`
    }).join('')
    return `<Row>${cells}</Row>`
  }).join('')

  const xml = `<?xml version="1.0"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
 <Worksheet ss:Name="Sheet1">
  <Table>
   <Row>${header}</Row>
   ${body}
  </Table>
 </Worksheet>
</Workbook>`

  downloadBlob(
    filename.endsWith('.xls') ? filename : `${filename}.xls`,
    new Blob([xml], { type: 'application/vnd.ms-excel;charset=utf-8;' }),
  )
}
