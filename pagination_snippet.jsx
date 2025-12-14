// Add this code to replace the pagination section starting around line 267

{/* Pagination Controls */ }
<div style={{
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: '20px',
    paddingTop: '16px',
    borderTop: '1px solid #334155',
    flexWrap: 'wrap',
    gap: '12px'
}}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span style={{ color: '#94a3b8', fontSize: '14px' }}>
            Showing {users.length} users (Page {currentPage})
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ color: '#94a3b8', fontSize: '13px' }}>Per page:</label>
            <select
                value={itemsPerPage}
                onChange={(e) => {
                    setItemsPerPage(Number(e.target.value));
                    setCurrentPage(1);
                }}
                style={{
                    padding: '6px 10px',
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '4px',
                    color: '#f8fafc',
                    fontSize: '13px'
                }}
            >
                <option value="10">10</option>
                <option value="20">20</option>
                <option value="50">50</option>
                <option value="100">100</option>
            </select>
        </div>
    </div>
    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
        <button
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            style={{
                padding: '8px 16px',
                background: currentPage === 1 ? '#1e293b' : '#334155',
                color: currentPage === 1 ? '#64748b' : '#f8fafc',
                border: '1px solid #334155',
                borderRadius: '6px',
                cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                fontSize: '14px'
            }}
        >
            ← Previous
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: '#94a3b8', fontSize: '13px' }}>Go to:</span>
            <input
                type="number"
                min="1"
                placeholder={currentPage.toString()}
                onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                        const page = parseInt(e.target.value);
                        if (page > 0) {
                            setCurrentPage(page);
                            e.target.value = '';
                        }
                    }
                }}
                style={{
                    width: '60px',
                    padding: '6px 10px',
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '4px',
                    color: '#f8fafc',
                    fontSize: '13px',
                    textAlign: 'center'
                }}
            />
        </div>
        <button
            onClick={() => setCurrentPage(prev => prev + 1)}
            disabled={users.length < itemsPerPage}
            style={{
                padding: '8px 16px',
                background: users.length < itemsPerPage ? '#1e293b' : '#334155',
                color: users.length < itemsPerPage ? '#64748b' : '#f8fafc',
                border: '1px solid #334155',
                borderRadius: '6px',
                cursor: users.length < itemsPerPage ? 'not-allowed' : 'pointer',
                fontSize: '14px'
            }}
        >
            Next →
        </button>
    </div>
</div>
