'use client';

import { useCallback, useEffect, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { ScreenNode } from './ScreenNode';
import type { ScreenData, SwimlaneAnalysis } from '@/store/swimlane-store';

// 节点类型映射
const nodeTypes = {
  screen: ScreenNode,
};

// 布局配置
const NODE_WIDTH = 120;
const NODE_HEIGHT = 280;
const HORIZONTAL_GAP = 40;
const VERTICAL_GAP = 40;
const SCREENS_PER_ROW = 10;

interface SwimlaneFlowProps {
  analysis: SwimlaneAnalysis;
  filteredScreens: ScreenData[];
  selectedScreen: ScreenData | null;
  onScreenSelect: (screen: ScreenData) => void;
  getImageUrl: (filename: string) => string;
}

/**
 * 泳道图流程组件 - 使用 React Flow 渲染截图网格
 */
export function SwimlaneFlow({
  analysis,
  filteredScreens,
  selectedScreen,
  onScreenSelect,
  getImageUrl,
}: SwimlaneFlowProps) {
  const typeColors = useMemo(() => {
    const colors: Record<string, string> = {};
    if (analysis?.summary?.by_type) {
      Object.entries(analysis.summary.by_type).forEach(([code, data]) => {
        colors[code] = data.color;
      });
    }
    return colors;
  }, [analysis]);

  // 生成节点数据
  const initialNodes = useMemo<Node[]>(() => {
    return filteredScreens.map((screen, idx) => {
      const row = Math.floor(idx / SCREENS_PER_ROW);
      const col = idx % SCREENS_PER_ROW;

      return {
        id: `screen-${screen.index}`,
        type: 'screen',
        position: {
          x: col * (NODE_WIDTH + HORIZONTAL_GAP),
          y: row * (NODE_HEIGHT + VERTICAL_GAP),
        },
        data: {
          ...screen,
          imageUrl: getImageUrl(screen.filename),
          isSelected: selectedScreen?.index === screen.index,
          typeColor: typeColors[screen.primary_type] || '#E5E5E5',
        },
      };
    });
  }, [filteredScreens, selectedScreen, typeColors, getImageUrl]);

  // 生成边数据（连接相邻节点）
  const initialEdges = useMemo<Edge[]>(() => {
    const edges: Edge[] = [];

    filteredScreens.forEach((screen, idx) => {
      if (idx < filteredScreens.length - 1) {
        const nextScreen = filteredScreens[idx + 1];
        const currentRow = Math.floor(idx / SCREENS_PER_ROW);
        const nextRow = Math.floor((idx + 1) / SCREENS_PER_ROW);

        // 同行内连接
        if (currentRow === nextRow) {
          edges.push({
            id: `edge-${screen.index}-${nextScreen.index}`,
            source: `screen-${screen.index}`,
            target: `screen-${nextScreen.index}`,
            type: 'smoothstep',
            style: { stroke: '#e5e7eb', strokeWidth: 2 },
          });
        }
      }
    });

    return edges;
  }, [filteredScreens]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // 同步外部数据变化
  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  // 节点点击处理
  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const screen = filteredScreens.find(
        (s) => `screen-${s.index}` === node.id
      );
      if (screen) {
        onScreenSelect(screen);
      }
    },
    [filteredScreens, onScreenSelect]
  );

  // MiniMap 节点颜色
  const nodeColor = useCallback(
    (node: Node) => {
      const data = node.data as ScreenData & { typeColor?: string };
      return data?.typeColor || '#E5E5E5';
    },
    []
  );

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{
          padding: 0.1,
          minZoom: 0.3,
          maxZoom: 1,
          nodes: nodes.slice(0, 30), // 只对前30个节点进行fitView，避免缩得太小
        }}
        minZoom={0.2}
        maxZoom={2}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#f0f0f0" gap={16} />
        <Controls position="bottom-left" />
        <MiniMap
          position="bottom-right"
          nodeColor={nodeColor}
          maskColor="rgba(0, 0, 0, 0.1)"
          style={{ backgroundColor: '#fff' }}
        />
      </ReactFlow>
    </div>
  );
}


