import React, { useEffect, useState } from 'react';

const MouseGlow = () => {
    const [position, setPosition] = useState({ x: 0, y: 0 });

    useEffect(() => {
        const handleMouseMove = (e) => {
            setPosition({ x: e.clientX, y: e.clientY });
        };

        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

    return (
        <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden transition-opacity duration-300">
            <div
                className="absolute w-[800px] h-[800px] rounded-full bg-primary/10 dark:bg-primary/20 blur-[120px]"
                style={{
                    transform: `translate(${position.x - 400}px, ${position.y - 400}px)`,
                    transition: 'transform 0.15s ease-out',
                }}
            />
        </div>
    );
};

export default MouseGlow;
