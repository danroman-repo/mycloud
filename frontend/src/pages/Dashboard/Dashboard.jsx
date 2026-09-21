import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useSearchParams } from 'react-router-dom';
import {
    fetchFiles,
    uploadFile,
    deleteFile,
    renameFile,
    updateComment,
    generateShareLink,
} from '../../store/slices/filesSlice';
import { filesAPI } from '../../api/client';
import styles from './Dashboard.module.css';

const Dashboard = () => {
    const dispatch = useDispatch();
    const { files, isLoading, error } = useSelector((state) => state.files);
    const { user } = useSelector((state) => state.auth);
    const [searchParams] = useSearchParams();
    const userIdParam = searchParams.get('user_id');

    const [showUploadForm, setShowUploadForm] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [comment, setComment] = useState('');
    const [editingFile, setEditingFile] = useState(null);
    const [newName, setNewName] = useState('');
    const [newComment, setNewComment] = useState('');

    useEffect(() => {
        const timer = setTimeout(() => {
            dispatch(fetchFiles(userIdParam));
        }, 500);

        return () => clearTimeout(timer);
    }, [dispatch, userIdParam]);

    const handleFileSelect = (e) => {
        setSelectedFile(e.target.files[0]);
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!selectedFile) return;

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('comment', comment);

        await dispatch(uploadFile(formData));
        setSelectedFile(null);
        setComment('');
        setShowUploadForm(false);
    };

    const handleDelete = async (fileId) => {
        if (window.confirm('Вы уверены, что хотите удалить этот файл?')) {
            await dispatch(deleteFile(fileId));
        }
    };

    const handleRename = async (fileId) => {
        if (newName.trim()) {
            await dispatch(renameFile({ fileId, displayName: newName }));
            setEditingFile(null);
            setNewName('');
        }
    };

    const handleUpdateComment = async (fileId) => {
        await dispatch(updateComment({ fileId, comment: newComment }));
        setEditingFile(null);
        setNewComment('');
    };

    const handleShare = async (fileId) => {
        await dispatch(generateShareLink(fileId));
    };

    const copyToClipboard = async (text) => {
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(text);
                alert('✅ Ссылка скопирована в буфер обмена!');
                return;
            }

            const textArea = document.createElement('textarea');
            textArea.value = text;

            textArea.style.position = 'fixed';
            textArea.style.top = '0';
            textArea.style.left = '0';
            textArea.style.width = '2em';
            textArea.style.height = '2em';
            textArea.style.padding = '0';
            textArea.style.border = 'none';
            textArea.style.outline = 'none';
            textArea.style.boxShadow = 'none';
            textArea.style.background = 'transparent';
            textArea.style.opacity = '0';

            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();

            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);

            if (successful) {
                alert('✅ Ссылка скопирована в буфер обмена!');
            } else {
                alert('❌ Не удалось скопировать ссылку. Скопируйте вручную: ' + text);
            }
        } catch (err) {
            console.error('Ошибка копирования:', err);
            alert('❌ Не удалось скопировать ссылку. Скопируйте вручную: ' + text);
        }
    };

    const handleDownload = (fileId) => {
        window.open(filesAPI.getDownloadUrl(fileId), '_blank');
    };

    const VIEWABLE_MIME_TYPES = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'image/svg+xml',
        'text/plain',
        'text/html',
        'video/mp4',
        'video/webm',
        'audio/mpeg',
        'audio/wav',
    ];

    const handleView = (fileId) => {
        window.open(filesAPI.getViewUrl(fileId), '_blank');
    };

    return (
        <div className={styles.dashboard}>
            <div className={styles.header}>
                <h1 className={styles.title}>Мои файлы</h1>
                <button
                    className="btn btn-primary"
                    onClick={() => setShowUploadForm(!showUploadForm)}
                >
                    {showUploadForm ? 'Отмена' : 'Загрузить файл'}
                </button>
            </div>

            {error &&
                <div className={styles.errorMessage}>
                    {error.message || 'Ошибка'}
                </div>
            }

            {showUploadForm && (
                <div className={styles.uploadForm}>
                    <form onSubmit={handleUpload}>
                        <div className={styles.formGroup}>
                            <label>Выберите файл:</label>
                            <input type="file" onChange={handleFileSelect} required />
                        </div>
                        <div className={styles.formGroup}>
                            <label>Комментарий:</label>
                            <textarea
                                value={comment}
                                onChange={(e) => setComment(e.target.value)}
                                rows="3"
                            />
                        </div>
                        <button
                            type="submit" className="btn btn-primary"
                            disabled={isLoading}
                        >
                            {isLoading ? 'Загрузка...' : 'Загрузить'}
                        </button>
                    </form>
                </div>
            )}

            {isLoading && <div className={styles.loading}>Загрузка...</div>}

            {!isLoading && files.length === 0 && (
                <div className={styles.emptyState}>
                    <p>У вас пока нет файлов. Загрузите первый файл!</p>
                </div>
            )}

            <div className={styles.filesList}>
                {files.map((file) => (
                    <div key={file.id} className={styles.fileCard}>
                        {editingFile === file.id ? (
                            <div className={styles.editForm}>
                                <input
                                    type="text"
                                    value={newName}
                                    onChange={(e) => setNewName(e.target.value)}
                                    placeholder="Новое имя файла"
                                />
                                <textarea
                                    value={newComment}
                                    onChange={(e) => setNewComment(e.target.value)}
                                    placeholder="Новый комментарий"
                                    rows="2"
                                />
                                <div className="edit-actions">
                                    <button
                                        className="btn btn-primary"
                                        onClick={() => {
                                            handleRename(file.id);
                                            handleUpdateComment(file.id);
                                        }}
                                    >
                                        Сохранить
                                    </button>
                                    <button
                                        className="btn btn-secondary"
                                        onClick={() => setEditingFile(null)}
                                    >
                                        Отмена
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <>
                                <div className={styles.fileInfo}>
                                    <h3 className={styles.fileName}>{file.display_name}</h3>
                                    <p className={styles.fileMeta}>
                                        <span>Размер: {file.size_formatted}</span>
                                        <span>Загружен: {new Date(file.uploaded_at).toLocaleString('ru-RU')}</span>
                                        {file.last_downloaded_at && (
                                            <span>
                                                Последнее скачивание:{' '}
                                                {new Date(file.last_downloaded_at).toLocaleString('ru-RU')}
                                            </span>
                                        )}
                                    </p>
                                    {file.comment && <p className={styles.fileComment}>{file.comment}</p>}
                                </div>

                                <div className={styles.fileActions}>
                                    <button className="btn btn-small" onClick={() => handleDownload(file.id)}>
                                        ⬇️ Скачать
                                    </button>

                                    {VIEWABLE_MIME_TYPES.includes(file.mime_type) && (
                                        <button
                                            className="btn btn-small btn-info"
                                            onClick={() => handleView(file.id)}
                                            title="Открыть файл в браузере"
                                        >
                                            👁️ Просмотр
                                        </button>
                                    )}

                                    <button
                                        className="btn btn-small"
                                        onClick={() => {
                                            setEditingFile(file.id);
                                            setNewName(file.display_name);
                                            setNewComment(file.comment);
                                        }}
                                    >
                                        ✏️ Редактировать
                                    </button>
                                    <button className="btn btn-small" onClick={() => handleShare(file.id)}>
                                        🔗 Поделиться
                                    </button>
                                    <button
                                        className="btn btn-small btn-danger"
                                        onClick={() => handleDelete(file.id)}
                                    >
                                        🗑️ Удалить
                                    </button>
                                </div>

                                {file.public_url && (
                                    <div className={styles.shareLink}>
                                        <input
                                            type="text"
                                            value={file.public_url}
                                            readOnly
                                            className={styles.shareInput}
                                        />
                                        <button
                                            className="btn btn-small"
                                            onClick={() => copyToClipboard(file.public_url)}
                                        >
                                            Копировать
                                        </button>
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Dashboard;