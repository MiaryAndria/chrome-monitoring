import React from 'react';
import { useMouseSpotlight } from '../utils/useMouseSpotlight';

export default function MouseSpotlight() {
    const { style } = useMouseSpotlight();

    return (
        <div 
            className="mouse-spotlight"
            style={style}
        />
    );
}
