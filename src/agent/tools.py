import datetime
import uuid
from abc import ABC, abstractmethod
import os
import logging
from typing import Dict, Any, List, Optional, BinaryIO, Union, Type
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """工具基类，所有工具都继承自此类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass

    @abstractmethod
    async def run(self, **kwargs) -> Dict[str, Any]:
        """运行工具"""
        pass


class ToolRegistry:
    """工具注册表，用于管理和实例化工具"""

    def __init__(self):
        """初始化工具注册表"""
        self._tools: Dict[str, Type[BaseTool]] = {}

    def register(self, tool_class: Type[BaseTool]) -> None:
        """
        注册工具类到注册表

        Args:
            tool_class: 要注册的工具类
        """
        # 创建临时实例获取名称
        instance = tool_class()
        tool_name = instance.name
        self._tools[tool_name] = tool_class
        logger.info(f"已注册工具: {tool_name}")

    def get_tool(self, tool_name: str, **kwargs) -> Optional[BaseTool]:
        """
        获取指定名称的工具实例

        Args:
            tool_name: 工具名称
            **kwargs: 传递给工具构造函数的参数

        Returns:
            工具实例或None（如果工具不存在）
        """
        tool_class = self._tools.get(tool_name)
        if not tool_class:
            logger.warning(f"未找到工具: {tool_name}")
            return None

        try:
            return tool_class(**kwargs)
        except Exception as e:
            logger.error(f"创建工具实例失败: {str(e)}")
            return None

    def list_tools(self) -> List[Dict[str, str]]:
        """
        列出所有已注册的工具

        Returns:
            工具信息列表，每个工具包含名称和描述
        """
        tools_info = []
        for tool_name, tool_class in self._tools.items():
            try:
                instance = tool_class()
                tools_info.append({
                    "name": tool_name,
                    "description": instance.description
                })
            except Exception as e:
                logger.error(f"获取工具信息失败: {tool_name}, 错误: {str(e)}")

        return tools_info

    def __contains__(self, tool_name: str) -> bool:
        """
        检查工具是否存在于注册表中

        Args:
            tool_name: 工具名称

        Returns:
            工具是否存在
        """
        return tool_name in self._tools

    def register_all(self, tool_classes: List[Type[BaseTool]]) -> None:
        """
        批量注册多个工具

        Args:
            tool_classes: 工具类列表
        """
        for tool_class in tool_classes:
            self.register(tool_class)


class DocumentStore(ABC):
    """文档存储接口，用于持久化文档数据"""

    @abstractmethod
    async def save_document(self,
                            document_id: str,
                            content: str,
                            metadata: Dict[str, Any],
                            file_path: Optional[str] = None) -> str:
        """
        保存文档到存储系统

        Args:
            document_id: 文档唯一ID
            content: 文档内容
            metadata: 文档元数据
            file_path: 原始文件路径(可选)

        Returns:
            文档ID
        """
        pass

    @abstractmethod
    async def get_document(self, document_id: str) -> Dict[str, Any]:
        """获取文档"""
        pass

    @abstractmethod
    async def list_documents(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """列出文档"""
        pass


class DatabaseDocumentStore(DocumentStore):
    """使用数据库实现的文档存储"""

    def __init__(self, db_connection_string: str):
        """
        初始化数据库文档存储

        Args:
            db_connection_string: 数据库连接字符串
        """
        self.db_connection_string = db_connection_string
        # 实际项目中需要初始化数据库连接
        # self.db_client = create_db_client(db_connection_string)
        logger.info("数据库文档存储已初始化")

    async def save_document(self,
                            document_id: str,
                            content: str,
                            metadata: Dict[str, Any],
                            file_path: Optional[str] = None) -> str:
        """
        保存文档到数据库
        """
        try:
            # 在实际实现中，这里会执行数据库插入操作
            # 例如: await self.db_client.documents.insert_one({...})

            # 构建要存储的文档对象
            doc_object = {
                "id": document_id,
                "content": content,
                "metadata": metadata,
                "original_file_path": file_path,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            }

            logger.info(f"文档已保存到数据库: {document_id}")
            return document_id

        except Exception as e:
            logger.error(f"保存文档到数据库失败: {str(e)}")
            raise

    async def get_document(self, document_id: str) -> Dict[str, Any]:
        """从数据库获取文档"""
        # 在实际实现中查询数据库
        # doc = await self.db_client.documents.find_one({"id": document_id})
        # return doc
        raise NotImplementedError("此方法需要在实际项目中实现")

    async def list_documents(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """列出符合条件的文档"""
        # 在实际实现中查询数据库
        # cursor = self.db_client.documents.find(filters or {})
        # return await cursor.to_list(length=100)
        raise NotImplementedError("此方法需要在实际项目中实现")


class PDFProcessTool(BaseTool):
    """处理PDF文档的工具，支持上传和内容提取，并保存到数据库"""

    def __init__(self,
                 document_store: Optional[DocumentStore] = None,
                 temp_dir: Optional[str] = None,
                 use_ocr: bool = True):
        """
        初始化PDF处理工具

        Args:
            document_store: 文档存储接口
            temp_dir: 临时文件存储目录，默认为系统临时目录
            use_ocr: 是否使用OCR进行图像文本识别
        """
        self.document_store = document_store
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.use_ocr = use_ocr
        os.makedirs(self.temp_dir, exist_ok=True)

    @property
    def name(self) -> str:
        return "pdf_processor"

    @property
    def description(self) -> str:
        return "上传和处理PDF文档，提取文本内容并保存到公司数据库"

    async def run(self, file_data: Union[BinaryIO, bytes], filename: str = None, **kwargs) -> Dict[str, Any]:
        """
        处理上传的PDF文件并保存到数据库

        Args:
            file_data: 文件数据流或二进制数据
            filename: 文件名

        Returns:
            Dict包含:
                - success: 是否成功
                - document_id: 存储的文档ID
                - text: 提取的文本
                - pages: 页面数
                - metadata: 文档元数据
        """
        try:
            import fitz  # PyMuPDF

            # 保存临时文件
            temp_file_path = self._save_temp_file(file_data, filename)

            # 打开PDF文档
            doc = fitz.open(temp_file_path)

            # 提取元数据
            metadata = {
                "title": doc.metadata.get("title", "") or filename or "未命名文档",
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "pages": len(doc),
                "format": "PDF",
                "filename": filename,
                "uploaded_at": datetime.datetime.now().isoformat(),
                "uploaded_by": kwargs.get("user_id", "unknown"),
                "file_size": os.path.getsize(temp_file_path)
            }

            # 提取文本内容
            text_content = ""
            for page_num, page in enumerate(doc):
                # 提取文本
                text = page.get_text()

                # 如果页面没有文本或文本很少，可能是扫描件，使用OCR
                if self.use_ocr and len(text.strip()) < 50:
                    text = await self._perform_ocr_on_page(page)

                text_content += f"\n--- 第{page_num + 1}页 ---\n{text}"

            # 关闭文档
            doc.close()

            # 生成唯一文档ID
            document_id = str(uuid.uuid4())

            # 保存到数据库
            if self.document_store:
                await self.document_store.save_document(
                    document_id=document_id,
                    content=text_content,
                    metadata=metadata,
                    file_path=temp_file_path if not kwargs.get("delete_temp", True) else None
                )

            # 可选：删除临时文件
            if kwargs.get("delete_temp", True):
                os.unlink(temp_file_path)

            return {
                "success": True,
                "document_id": document_id,
                "text": text_content,
                "pages": metadata["pages"],
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"PDF处理失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _save_temp_file(self, file_data: Union[BinaryIO, bytes], filename: Optional[str]) -> str:
        """保存上传文件到临时目录"""
        filename = filename or f"uploaded_pdf_{os.urandom(4).hex()}.pdf"
        file_path = os.path.join(self.temp_dir, filename)

        if isinstance(file_data, bytes):
            with open(file_path, "wb") as f:
                f.write(file_data)
        else:
            with open(file_path, "wb") as f:
                f.write(file_data.read())

        logger.info(f"临时PDF文件已保存: {file_path}")
        return file_path

    async def _perform_ocr_on_page(self, page) -> str:
        """对PDF页面进行OCR处理"""
        try:
            import pytesseract
            from PIL import Image

            # 将页面渲染为图片
            pix = page.get_pixmap()
            img_path = os.path.join(self.temp_dir, f"temp_page_{os.urandom(4).hex()}.png")
            pix.save(img_path)

            # 使用pytesseract进行OCR
            img = Image.open(img_path)
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')  # 中文+英文

            # 清理临时文件
            os.unlink(img_path)

            return text
        except Exception as e:
            logger.warning(f"OCR处理失败: {str(e)}")
            return ""


# 创建全局工具注册表实例
default_registry = ToolRegistry()

# 注册默认工具
default_registry.register(PDFProcessTool)

# 兼容旧版API的函数
def get_tool(tool_name: str, document_store: Optional[DocumentStore] = None, **kwargs) -> Optional[BaseTool]:
    """获取指定名称的工具实例（兼容旧版API）"""
    if tool_name == "pdf_processor" and document_store:
        kwargs["document_store"] = document_store
    return default_registry.get_tool(tool_name, **kwargs)


def list_available_tools() -> List[Dict[str, str]]:
    """列出所有可用的工具（兼容旧版API）"""
    return default_registry.list_tools()