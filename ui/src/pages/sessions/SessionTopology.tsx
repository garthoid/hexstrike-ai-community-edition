import { useMemo } from 'react'
import { ReactFlow, Background, Controls, MiniMap, type Node, type Edge } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import type { SessionSummary, TopologyHost, TopologyPort } from '../../api'
import './SessionTopology.css'

const HOST_X = 40
const PORT_X = 340
const ROW_H = 56

const STATE_COLORS: Record<string, string> = {
  open: 'var(--success, #2ecc71)',
  filtered: 'var(--warning, #f0b429)',
  closed: 'var(--text-dim, #4a5568)',
}

function stateColor(state: string): string {
  return STATE_COLORS[state.toLowerCase()] ?? 'var(--border, #252836)'
}

function HostLabel({ host }: { host: TopologyHost }) {
  return (
    <div className="topology-node-label">
      <strong className="mono">{host.ip}</strong>
      {host.hostname && <span className="section-meta">{host.hostname}</span>}
      {host.mac && <span className="section-meta mono">{host.mac}{host.vendor ? ` (${host.vendor})` : ''}</span>}
    </div>
  )
}

function PortLabel({ port }: { port: TopologyPort }) {
  return (
    <div className="topology-node-label">
      <strong className="mono">{port.port}/{port.protocol}</strong>
      <span className="section-meta">{port.service ?? 'unknown'} · {port.state}</span>
      {port.version && <span className="section-meta">{port.version}</span>}
    </div>
  )
}

function buildGraph(hosts: TopologyHost[], ports: TopologyPort[]): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = []
  const edges: Edge[] = []
  let hostY = 40

  for (const host of hosts) {
    const hostId = `host:${host.ip}`
    nodes.push({
      id: hostId,
      position: { x: HOST_X, y: hostY },
      data: { label: <HostLabel host={host} /> },
      style: {
        background: 'var(--bg-card2)',
        border: '1px solid var(--accent)',
        borderRadius: 8,
        padding: 4,
        width: 260,
      },
    })

    const hostPorts = ports
      .filter(p => p.host === host.ip)
      .sort((a, b) => a.port - b.port)

    let portY = hostY
    for (const port of hostPorts) {
      const portId = `port:${host.ip}:${port.port}:${port.protocol}`
      nodes.push({
        id: portId,
        position: { x: PORT_X, y: portY },
        data: { label: <PortLabel port={port} /> },
        style: {
          background: 'var(--bg-card)',
          border: `2px solid ${stateColor(port.state)}`,
          borderRadius: 8,
          padding: 4,
          width: 220,
        },
      })
      edges.push({
        id: `${hostId}->${portId}`,
        source: hostId,
        target: portId,
        style: { stroke: 'var(--border)' },
      })
      portY += ROW_H
    }

    hostY += Math.max(hostPorts.length, 1) * ROW_H + 40
  }

  return { nodes, edges }
}

export function SessionTopology({ session }: { session: SessionSummary }) {
  const topology = session.topology
  const { nodes, edges } = useMemo(
    () => buildGraph(topology?.hosts ?? [], topology?.ports ?? []),
    [topology]
  )

  if (!topology || topology.hosts.length === 0) {
    return (
      <div className="session-topology">
        <p className="empty-state">
          No topology data yet — run nmap from the Run page (or a step in this session) and export the result to the topology map.
        </p>
      </div>
    )
  }

  return (
    <div className="session-topology">
      <div className="session-topology-meta section-meta">
        {topology.hosts.length} host{topology.hosts.length === 1 ? '' : 's'} · {topology.ports.length} port{topology.ports.length === 1 ? '' : 's'}
        {topology.updated_at ? ` · updated ${new Date(topology.updated_at * 1000).toLocaleString()}` : ''}
      </div>
      <div className="session-topology-canvas">
        <ReactFlow nodes={nodes} edges={edges} fitView proOptions={{ hideAttribution: true }}>
          <Background />
          <Controls showInteractive={false} />
          <MiniMap
            pannable
            zoomable
            bgColor="var(--bg-card2)"
            maskColor="color-mix(in srgb, var(--bg) 65%, transparent)"
            nodeColor="var(--bg-card)"
            nodeStrokeColor="var(--border)"
          />
        </ReactFlow>
      </div>
    </div>
  )
}
