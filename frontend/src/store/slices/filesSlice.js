import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { filesAPI } from '../../api/client';

export const fetchFiles = createAsyncThunk(
    'files/fetchFiles',
    async (userId = null, { rejectWithValue }) => {
        try {
            const response = await filesAPI.getAll(userId);
            return response.data;
        } catch (error) {
            return rejectWithValue(error.response?.data || { message: 'Ошибка получения файлов' });
        }
    }
);

export const uploadFile = createAsyncThunk(
    'files/uploadFile',
    async (formData, { rejectWithValue }) => {
        try {
            const response = await filesAPI.upload(formData);
            return response.data;
        } catch (error) {
            return rejectWithValue(error.response?.data || { message: 'Ошибка загрузки файла' });
        }
    }
);

export const deleteFile = createAsyncThunk(
    'files/deleteFile',
    async (fileId, { rejectWithValue }) => {
        try {
            await filesAPI.delete(fileId);
            return fileId;
        } catch (error) {
            return rejectWithValue(error.response?.data || { message: 'Ошибка удаления файла' });
        }
    }
);

export const renameFile = createAsyncThunk(
    'files/renameFile',
    async ({ fileId, displayName }, { rejectWithValue }) => {
        try {
            const response = await filesAPI.rename(fileId, displayName);
            return response.data;
        } catch (error) {
            return rejectWithValue(error.response?.data || { message: 'Ошибка переименования' });
        }
    }
);

export const updateComment = createAsyncThunk(
    'files/updateComment',
    async ({ fileId, comment }, { rejectWithValue }) => {
        try {
            const response = await filesAPI.updateComment(fileId, comment);
            return response.data;
        } catch (error) {
            return rejectWithValue(error.response?.data || { message: 'Ошибка обновления комментария' });
        }
    }
);

export const generateShareLink = createAsyncThunk(
    'files/generateShareLink',
    async (fileId, { rejectWithValue }) => {
        try {
            const response = await filesAPI.share(fileId);
            return response.data;
        } catch (error) {
            return rejectWithValue(error.response?.data || { message: 'Ошибка генерации ссылки' });
        }
    }
);

const filesSlice = createSlice({
    name: 'files',
    initialState: {
        files: [],
        isLoading: false,
        error: null,
    },
    reducers: {
        clearError: (state) => {
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchFiles.pending, (state) => {
                state.isLoading = true;
                state.error = null;
            })
            .addCase(fetchFiles.fulfilled, (state, action) => {
                state.isLoading = false;
                state.files = action.payload;
            })
            .addCase(fetchFiles.rejected, (state, action) => {
                state.isLoading = false;
                if (action.payload?.status_code === 403) {
                    state.error = null;
                } else {
                    state.error = action.payload;
                }
            })
            .addCase(uploadFile.fulfilled, (state, action) => {
                state.files.unshift(action.payload);
            })
            .addCase(deleteFile.fulfilled, (state, action) => {
                state.files = state.files.filter(file => file.id !== action.payload);
            })
            .addCase(renameFile.fulfilled, (state, action) => {
                const index = state.files.findIndex(file => file.id === action.payload.id);
                if (index !== -1) {
                    state.files[index] = action.payload;
                }
            })
            .addCase(updateComment.fulfilled, (state, action) => {
                const index = state.files.findIndex(file => file.id === action.payload.id);
                if (index !== -1) {
                    state.files[index] = action.payload;
                }
            })
            .addCase(generateShareLink.fulfilled, (state, action) => {
                const index = state.files.findIndex(file => file.id === action.payload.id);
                if (index !== -1) {
                    state.files[index] = action.payload;
                }
            });
    },
});

export const { clearError } = filesSlice.actions;
export default filesSlice.reducer;